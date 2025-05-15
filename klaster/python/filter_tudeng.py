import os
import time
import sys
import estnltk
import multiprocessing as mp

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

from words_tokenization import preprocess_words
from sentence_tokenization import sentence_tokenizer
from sentence_tokenization import postfix_sentence_breaks_inside_parentheses

def process(name, input_folder, output_folder):
    with open(input_folder + "/" + name, "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    
    #vana lausestus ja sõnestus maha
    text_import.pop_layer('sentences')
    text_import.pop_layer('words')
    text_import.pop_layer('compound_tokens')

    #uus lausestus ja sõnestus
    preprocess_words( text_import )
    sentence_tokenizer.tag( text_import )
    postfix_sentence_breaks_inside_parentheses( text_import, doc_name='' )

    text_to_json(text_import, file=(output_folder + "/" + name))

if __name__ == '__main__':
    input_folder = 'data/tudengid'
    output_folder = 'data/processed_tudengid'
    os.makedirs(output_folder, exist_ok=True)

    gold = {'1922-04-24.json', '1936-09-07.json', '1927-03-28.json', '1941-01-03.json', '1932-01-25.json', '1934-10-15.json', '1935-09-30.json'}

    file_args = []
    start_time = time.time()

    for name in os.listdir(input_folder):
        if name in gold:
            continue
        file_args.append((name, input_folder, output_folder))

    num_cores = int(sys.argv[2])
    print(f"Using {num_cores} CPU cores")
    
    with mp.Pool(processes=num_cores) as pool:
        results = pool.starmap(process, file_args)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Filter - Elapsed time: {elapsed_time:.4f} seconds")
    print(len(os.listdir(input_folder)), len(os.listdir(output_folder)), len(gold), len(os.listdir(input_folder)) - len(os.listdir(output_folder)))