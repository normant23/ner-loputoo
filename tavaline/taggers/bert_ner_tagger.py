#
#  EstNLTK's Tagger for BERT-based named entity recognition.
#  Original source: https://github.com/soras/vk_ner_lrec_2022
#
#  Requirements:
#     estnltk      v1.7.0+
#     pytorch      v1.7.0+
#     transformers v4.0.0+
#     sentencepiece
#

import re
import os, os.path

from typing import MutableMapping, List

from estnltk.text import Text
from estnltk.taggers import Tagger
from estnltk import Layer

import torch
import numpy as np
from transformers import AutoConfig
from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification

def _is_model_from_huggingface( model_path_or_name: str ):
    '''
    Checks if the given model_path_or_name is an existing model in huggingface.co.
    Returns True if such model exists and False otherwise.
    '''
    from huggingface_hub import model_info
    from requests.exceptions import HTTPError
    try:
        model_inf = model_info(model_path_or_name)
        return True
    except HTTPError as err:
        status_code = err.response.status_code
        if status_code == 404:
            # URL not found: no such model exists in hf
            return False
        raise err


class BertNERTagger(Tagger):
    """Applies BERT-based named entity recognition."""

    def __init__( self, 
                  bert_tokenizer_location: str, 
                  bert_ner_location: str, 
                  output_layer: str = 'bert_ner',
                  sentences_layer: str = 'sentences',
                  token_level: bool = False,
                  ignore_sentence_boundaries: bool = True,
                  ambiguous_label_separator:str = '|',
                  **kwargs ):
        assert bert_tokenizer_location is not None
        assert bert_ner_location is not None
        # Check if we have a local model or a huggingface model
        if not os.path.exists( bert_tokenizer_location ):
            if not _is_model_from_huggingface( bert_tokenizer_location ):
                raise ValueError( ('(!) Invalid bert_tokenizer_location={!r}. '+\
                                   'It should be either a path to the local model '+\
                                   'directory or repo_id of a model available '+\
                                   'from huggingface.co').format( bert_tokenizer_location ) )
        if not os.path.exists( bert_ner_location ):
            if not _is_model_from_huggingface( bert_ner_location ):
                raise ValueError( ('(!) Invalid bert_ner_location={!r}. '+\
                                   'It should be either a path to the local model '+\
                                   'directory or repo_id of a model available '+\
                                   'from huggingface.co').format( bert_tokenizer_location ) )
        self.conf_param = ('bert_tokenizer', 'bert_ner', 'sentences_layer', 'token_level', 
                           'id2label', 'merge_consecutive_tags', 'ignore_sentence_boundaries',
                           'ambiguous_label_separator')
        tokenizer_kwargs = { k:v for (k,v) in kwargs.items() if k in ['do_lower_case', 'use_fast'] }
        self.bert_tokenizer = AutoTokenizer.from_pretrained( bert_tokenizer_location, **tokenizer_kwargs )
        self.bert_ner = AutoModelForTokenClassification.from_pretrained( bert_ner_location,
            output_attentions = False,
            output_hidden_states = False )
        # Fetch id2label mapping from configuration
        config_dict = AutoConfig.from_pretrained(bert_ner_location).to_dict()
        self.id2label, _ = config_dict["id2label"], config_dict["label2id"]
        # Set input and output layers
        self.token_level = token_level
        self.sentences_layer = sentences_layer
        self.output_layer = output_layer
        self.input_layers = [sentences_layer]
        self.output_attributes = ['bert_tokens', 'nertag']
        self.ambiguous_label_separator = ambiguous_label_separator
        # Ignores sentence boundaries intersecting with ner phrases
        # ( because frequently sentence boundaries are wrong, and ner phrases are correct )
        self.ignore_sentence_boundaries = ignore_sentence_boundaries
    
    def _get_bert_ner_label_predictions(self, input_str):
        '''Applies Bert on given input string and returns Bert's tokens, token indexes and predicted NER labels.'''
        token_indexes = self.bert_tokenizer.encode(input_str)
        input_ids = torch.tensor([token_indexes])
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.bert_ner.to(device)
        input_ids = input_ids.to(device)
        assert not len(input_ids) > 512 # TODO: maximum sequence length can be 512
        with torch.no_grad():
            output = self.bert_ner(input_ids)
        tokens = self.bert_tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
        label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)
        converted_labels = [self.id2label[l] if l in self.id2label else f'---({l})' for l in label_indices[0]]
        assert len(tokens) == len(token_indexes)
        assert len(converted_labels) == len(token_indexes)
        return tokens, token_indexes, converted_labels


    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        sentences_layer = layers[ self.sentences_layer ]
        bert_ner_layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                                 ambiguous=True)
        # Note: sentence tokenization can be wrong. Therefore, collect token level annotations
        # regardless of the sentence boundaries
        token_level_annotations = []
        for k, sentence in enumerate( sentences_layer ):
            sent_start = sentence.start
            sent_text  = sentence.enclosing_text
            # Apply batch processing: split larger input sentence into smaller chunks and 
            # process chunk by chunk
            sent_chunks, sent_chunk_indexes = _split_sentence_into_smaller_chunks( sent_text )
            for sent_chunk, (chunk_start, chunk_end) in zip(sent_chunks, sent_chunk_indexes):
                # Get predictions for the sentence
                tokens, token_indexes, converted_labels = self._get_bert_ner_label_predictions( sent_chunk )
                tokens_with_indexes = get_tokens_with_start_end_indexes(sent_chunk, 
                                                                        self.bert_tokenizer, 
                                                                        token_indexes,
                                                                        tokens,
                                                                        bert_token_labels=converted_labels,
                                                                        subtokenize=True)
                # Collect token level annotations (a label for each token)
                for token_id, token_data in enumerate( tokens_with_indexes ):
                    start, end  = token_data[-1]
                    bert_tokens = token_data[1]
                    labels = list(set(token_data[2]))
                    single_label = \
                        labels[0] if len(labels) < 2 else (self.ambiguous_label_separator).join( labels )
                    clean_labels = [ l[2:] if l != 'O' else 'O' for l in labels ]
                    annotation = {'bert_tokens' : bert_tokens, 'nertag' : single_label }
                    conflicts_sentence = False
                    if token_id == 0 and single_label.startswith(('I_', 'I-')):
                        conflicts_sentence = True
                    token_level_annotations.append( [ sent_start + chunk_start + start, 
                                                      sent_start + chunk_start + end, \
                                                                    annotation, clean_labels, 
                                                                    conflicts_sentence ] )
        # Add annotations
        if self.token_level:
            # Mark token level annotations (a label for each token)
            for [start, end, annotation, cl_labels, conflicts_sentence] in token_level_annotations:
                bert_ner_layer.add_annotation( (start, end), **annotation )
        else: 
            # Collect named entity phrases
            ner_phrases = []
            cur_phrase = None
            for [start, end, annotation, cl_labels, conflicts_sentence] in token_level_annotations:
                wordlevel_tag = annotation['nertag']
                if wordlevel_tag.startswith(('B_', 'B-')):
                    # Empty the buffer
                    if cur_phrase is not None:
                        ner_phrases.append( cur_phrase )
                        cur_phrase = None
                    # Start a new phrase
                    cur_phrase = { 'start': start, 'end': end, 'bert_tokens': annotation['bert_tokens'], 
                                   'labels' : [wordlevel_tag], 'clean_labels':cl_labels }
                elif wordlevel_tag.startswith(('I_', 'I-')):
                    if conflicts_sentence and not self.ignore_sentence_boundaries:
                        # Empty the buffer
                        if cur_phrase is not None:
                            ner_phrases.append( cur_phrase )
                            cur_phrase = None
                        # Start a new phrase
                        cur_phrase = { 'start': start, 'end': end, 'bert_tokens': annotation['bert_tokens'], 
                                       'labels' : [wordlevel_tag], 'clean_labels':cl_labels }
                    else:
                        same_tag_continued = False
                        if cur_phrase is not None:
                            if cur_phrase['clean_labels'][-1] == cl_labels[0]:
                                # Continue phrase with the same tag
                                cur_phrase['end'] = end
                                cur_phrase['bert_tokens'].extend( annotation['bert_tokens'] )
                                cur_phrase['labels'].extend([wordlevel_tag])
                                cur_phrase['clean_labels'].extend(cl_labels)
                                same_tag_continued = True
                        if not same_tag_continued:
                            # Empty the buffer
                            if cur_phrase is not None:
                                ner_phrases.append( cur_phrase )
                                cur_phrase = None
                            # Start a new phrase
                            cur_phrase = { 'start': start, 'end': end, 'bert_tokens': annotation['bert_tokens'], 
                                           'labels' : [wordlevel_tag], 'clean_labels':cl_labels }
                else:
                    assert wordlevel_tag.startswith('O')
                    # Empty the buffer
                    if cur_phrase is not None:
                        ner_phrases.append( cur_phrase )
                        cur_phrase = None
            # Empty the buffer last time
            if cur_phrase is not None:
                ner_phrases.append( cur_phrase )
                cur_phrase = None
            # Add phrases to the layer
            for phrase in ner_phrases:
                start, end  = phrase['start'], phrase['end']
                assert len(labels) > 0
                labels = list(set([l for l in phrase['clean_labels'] if l != 'O']))
                single_label = \
                    labels[0] if len(labels) < 2 else (self.ambiguous_label_separator).join( labels )
                annotation = {'bert_tokens' : phrase['bert_tokens'], 'nertag' : single_label }
                bert_ner_layer.add_annotation( (start, end), **annotation )
        return bert_ner_layer

def _split_sentence_into_smaller_chunks(large_sent: str, max_size:int=1000, seek_end_symbols: str='.!?'):
    '''Splits given large_sent into smaller texts following the text size limit. 
       Each smaller text string is allowed to have at most `max_size` characters.
       Returns smaller text strings and their (start, end) indexes in the large_sent.
    '''
    assert max_size > 0, f'(!) Invalid batch size: {max_size}'
    if len(large_sent) < max_size:
        return [large_sent], [(0, len(large_sent))]
    chunks = []
    chunk_separators = []
    chunk_indexes = []
    last_chunk_end = 0
    while last_chunk_end < len(large_sent):
        chunk_start = last_chunk_end
        chunk_end = chunk_start + max_size
        if chunk_end >= len(large_sent):
            chunk_end = len(large_sent)
        if isinstance(seek_end_symbols, str):
            # Heuristic: Try to find the last position in the chunk that 
            # resembles sentence ending (matches one of the seek_end_symbols)
            i = chunk_end - 1
            while i > chunk_start + 1:
                char = large_sent[i]
                if char in seek_end_symbols:
                    chunk_end = i + 1
                    break
                i -= 1
        chunks.append( large_sent[chunk_start:chunk_end] )
        chunk_indexes.append( (chunk_start, chunk_end) )
        # Find next chunk_start, skip space characters
        updated_chunk_end = chunk_end
        if chunk_end != len(large_sent):
            i = chunk_end
            while i < len(large_sent):
                char = large_sent[i]
                if not char.isspace():
                    updated_chunk_end = i
                    break
                i += 1
            chunk_separators.append( large_sent[chunk_end:updated_chunk_end] )
        last_chunk_end = updated_chunk_end
    assert len(chunk_separators) == len(chunks) - 1
    # Return extracted chunks
    return ( chunks, chunk_indexes )

def get_word_subtoken_indexes( w_string, w_bert_tokens, w_bert_indexes, w_bert_labels=None ):
    '''Finds start/end positions of Bert's tokens, token indexes and predicted NER labels in a word token (w_string).
       Returns a list of packaged tokens and positions. Each list item is in the form:
          ((subtoken_start, subtoken_end), subtoken_bert_tokens, subtoken_bert_indexes, subtoken_bert_labels)
    '''
    i = 0
    j = 0
    subtokens = []
    mismatch = False
    while i < len(w_string)  and  j < len(w_bert_tokens):
        w_bert_token = w_bert_tokens[j][:]
        w_bert_index = w_bert_indexes[j]
        w_bert_label = w_bert_labels[j] if w_bert_labels else None
        if w_bert_token.startswith("##"):
            # Bert
            w_bert_token = w_bert_token[2:]
        elif w_bert_token.startswith('▁'):
            # RobertA
            w_bert_token = w_bert_token[1:]
        word_chunk = w_string[ i:i+len(w_bert_token) ]
        if word_chunk == w_bert_token:
            location = ( i, i+len(w_bert_token) )
            subtokens.append( ( location, [w_bert_tokens[j]], [w_bert_index], [w_bert_label] ) )
            i += len(w_bert_token)-1
            j += 1
        elif word_chunk.startswith(' '):
            # Attempt to skip the whitespace
            i += 1
            continue
        else:
            mismatch = True
            break
        i += 1
    if mismatch:
        # Failed to match substrings: take the whole string
        location = ( 0, len(w_string) )
        subtokens = [( location, w_bert_tokens, w_bert_indexes, w_bert_labels )]
    return subtokens

pattern_nonspace = re.compile('\S+')

def get_tokens_with_start_end_indexes(input_str, tokenizer, bert_token_indexes, bert_tokens, 
                                      bert_token_labels=None, subtokenize=False):
    '''Finds start/end positions of Bert's tokens, token indexes and predicted NER labels in the original input_str.
       Returns a list of packaged tokens and positions. Each list item is in the form:
          [ word_token_indexes, word_bert_tokens, word_token_labels, (start, end) ]
    '''
    # Validate input size
    assert len(bert_token_indexes) == len(bert_tokens)
    if bert_token_labels:
        assert len(bert_token_indexes) == len(bert_token_labels)
    # EstBert
    if bert_token_indexes[0] == 2 and bert_token_indexes[-1] == 3:
        # Remove special tokens [CLS] and [SEP]
        bert_token_indexes = bert_token_indexes[1:-1]
        bert_tokens = bert_tokens[1:-1]
        if bert_token_labels:
            bert_token_labels = bert_token_labels[1:-1]
    if len(bert_tokens) > 0:
        # FinEstEngBert
        if bert_tokens[0] == '[CLS]' and bert_tokens[-1] == '[SEP]':
            # Remove special tokens
            bert_token_indexes = bert_token_indexes[1:-1]
            bert_tokens = bert_tokens[1:-1]
            if bert_token_labels:
                bert_token_labels = bert_token_labels[1:-1]
    if len(bert_tokens) > 0:
        # EstRoberta
        if bert_tokens[0] == '<s>' and bert_tokens[-1] == '</s>':
            # Remove special tokens <s> and </s>
            bert_token_indexes = bert_token_indexes[1:-1]
            bert_tokens = bert_tokens[1:-1]
            if bert_token_labels:
                bert_token_labels = bert_token_labels[1:-1]
    # 1) Split text into tokens by spaces and get locations
    #    of the tokens; 
    # 2) Align tokens with bert tokens, bert token indexes 
    #    and corresponding labels;
    # Inspired by cronoik's post @ stackoverflow ( https://stackoverflow.com/a/63422347 )
    indexes = []
    i = 0
    for m in re.finditer(r'\S+', input_str):
      w = m.group(0)
      start = m.start()
      end = m.end()
      word_token_indexes = tokenizer.encode(w, add_special_tokens=False)
      j = 0
      word_bert_tokens = []
      word_token_labels = []
      while i < len(bert_token_indexes) and j < len(word_token_indexes):
        word_token_index = word_token_indexes[j]
        bert_token_index = bert_token_indexes[i]
        bert_token = bert_tokens[i]
        word_bert_tokens.append( bert_token )
        if word_token_index != bert_token_index:
            raise ValueError('(!) Tokens mismatch at ', (start, end) )
        if bert_token_labels:
            word_token_labels.append( bert_token_labels[i] )
        i += 1
        j += 1
      if not subtokenize:
            t = [ word_token_indexes, word_bert_tokens, word_token_labels, (start, end) ]
            indexes.append(t)
      else:
            subtokens = get_word_subtoken_indexes( w,word_bert_tokens,word_token_indexes,word_token_labels )
            for ((sub_start, sub_end), sub_bert_tokens, sub_bert_indexes, sub_bert_labels) in subtokens:
                t = [ sub_bert_indexes,sub_bert_tokens,sub_bert_labels,(start+sub_start,start+sub_end) ]
                indexes.append(t)
    return indexes