import os
import time
import estnltk
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

from words_tokenization import preprocess_words
from sentence_tokenization import sentence_tokenizer
from sentence_tokenization import postfix_sentence_breaks_inside_parentheses

from estnltk_core.layer_operations import extract_sections
from estnltk_core.layer_operations import join_texts

input_folder = 'data/koik'
output_folder = 'data/uus_koik'

gold = {'1922-04-24.json', '1936-09-07.json', '1927-03-28.json', '1941-01-03.json', '1932-01-25.json', '1934-10-15.json', '1935-09-30.json'}

start_time = time.time()
for name in os.listdir(input_folder):
    if name in gold:
        continue
    with open(input_folder + "/" + name, "r", encoding="utf-8") as file:
        content = file.read()
    text_import = json_to_text(json_text=content)

    indexes = [text_import.words[0].start]
    for table in text_import.table_regions:
        indexes.extend([table.start, table.end])
    indexes.append(text_import.words[-1].end)

    if len(indexes) > 2:
        pairs = [(indexes[i], indexes[i+1]) for i in range(0, len(indexes), 2)]
        texts = extract_sections(text=text_import, sections=pairs)
        text_joined = join_texts(texts)
        text_import = text_joined
    
    #vana lausestus ja sõnestus maha
    text_import.pop_layer('sentences')
    text_import.pop_layer('words')
    text_import.pop_layer('compound_tokens')

    #uus lausestus ja sõnestus
    preprocess_words( text_import )
    sentence_tokenizer.tag( text_import )
    postfix_sentence_breaks_inside_parentheses( text_import, doc_name='' )

    text_to_json(text_import, file=(output_folder + "/" + name))

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Filter - Elapsed time: {elapsed_time:.4f} seconds")
print(len(os.listdir(input_folder)), len(os.listdir(output_folder)), len(gold), len(os.listdir(input_folder)) - len(os.listdir(output_folder)))