import estnltk
import os
import sys
import time
import pandas as pd
import multiprocessing as mp

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

def verify_sen(text, start, end):
    current = ''
    for nr, span in enumerate(text.new2_ner[start:end]):
        if span.nertag == 'O':
            current = 'O'
        elif span.nertag.startswith('B-'):
            current = span.nertag[-3:]
        elif span.nertag.startswith('I-'):
            if current != span.nertag[-3:]:
                return nr
    return -1

def process(limit, name, input_folder, output_folder):
    with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    
    last_index = 0
    
    for sen in text_import.sentences:
        change = verify_sen(text_import, last_index, last_index + len(sen.text))
        while change != -1:
            if text_import.new2_ner[last_index + change].prob >= limit:
                text_import.new2_ner[last_index + change].annotations[0]['nertag'] = 'B-' + text_import.new2_ner[last_index + change].nertag[-3:]
            else:
                text_import.new2_ner[last_index + change].annotations[0]['nertag'] = 'O'
            change = verify_sen(text_import, last_index, last_index + len(sen.text))

        last_index += len(sen.text)

    text_to_json(text_import, file=(output_folder + "/" + name))

if __name__ == '__main__':
    model_name = sys.argv[2]
    input_folder = f'data/first_model_tagged/{model_name}'
    output_folder = f'data/first_model_tagged_clean/{model_name}'
    os.makedirs(output_folder, exist_ok=True)
    limit = 0.8
    file_args = []

    start_time = time.time()

    for name in os.listdir(input_folder):
        file_args.append((limit, name, input_folder, output_folder))

    num_cores = int(sys.argv[3])
    print(f"Using {num_cores} CPU cores")
    
    with mp.Pool(processes=num_cores) as pool:
        results = pool.starmap(process, file_args)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Clean - Elapsed time: {elapsed_time:.4f} seconds")
