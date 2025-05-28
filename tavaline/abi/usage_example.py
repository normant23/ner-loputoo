from estnltk import Text

# Import adapted words tokenization
from words_tokenization import preprocess_words

# Import adapted sentence tokenizer
from sentence_tokenization import sentence_tokenizer
from sentence_tokenization import postfix_sentence_breaks_inside_parentheses

text_obj = Text('Ln.W.Tamman ja Pr. E.Tomson võtsid koos ühe kläfi.')
preprocess_words( text_obj )
sentence_tokenizer.tag( text_obj )
postfix_sentence_breaks_inside_parentheses( text_obj, doc_name='' )

for word in text_obj.words:
    print(word.text)