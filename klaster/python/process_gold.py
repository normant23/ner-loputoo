import estnltk
import os

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

from words_tokenization import preprocess_words
from sentence_tokenization import sentence_tokenizer
from sentence_tokenization import postfix_sentence_breaks_inside_parentheses

input_folder = 'data/gold'
output_folder = 'data/processed_gold'

for name in os.listdir(input_folder):
    with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
        content = file.read()
    text_import = json_to_text(json_text=content)

    text_import.pop_layer('sentences')
    text_import.pop_layer('words')

    preprocess_words( text_import )
    sentence_tokenizer.tag( text_import )
    postfix_sentence_breaks_inside_parentheses( text_import, doc_name='' )

    if name == '1934-10-15_manual_annotated.json':
        #htusegümnaasiumi -> õhtusegümnaasiumi
        print(text_import.ne_gold_a[642], text_import.ne_gold_a[642].start)
        text_import.ne_gold_a.remove_span(text_import.ne_gold_a[642])
        text_import.ne_gold_a.add_annotation( text_import.words[7005].base_span, {'tag': 'ORG'})
        print(text_import.ne_gold_a[642], text_import.ne_gold_a[642].start)
    
    if name == '1935-09-30_manual_annotated.json':
        #Rosenfeldt -> J.Rosenfeldt
        print(text_import.ne_gold_a[431], text_import.ne_gold_a[431].start)
        text_import.ne_gold_a.remove_span(text_import.ne_gold_a[431])
        text_import.ne_gold_a.add_annotation( text_import.words[6679].base_span, {'tag': 'PER'})
        print(text_import.ne_gold_a[431], text_import.ne_gold_a[431].start)

        #majõevaheline plats -> Emajõevaheline plats
        print(text_import.ne_gold_a[597], text_import.ne_gold_a[597].start)
        text_import.ne_gold_a.remove_span(text_import.ne_gold_a[597])
        text_import.ne_gold_a.add_annotation( (54117, 54137), {'tag': 'LOC'})
        print(text_import.ne_gold_a[597], text_import.ne_gold_a[597].start)
    
    text_to_json(text_import, file=(output_folder + "/" + name))