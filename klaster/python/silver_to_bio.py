import estnltk
import os
import sys
import time
import pandas as pd
import multiprocessing as mp

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

def process(csv, input_folder, output_folder, text_folder):
    bio = pd.DataFrame(columns=['sentence_id', 'words', 'labels'])
    silver = pd.read_csv(os.path.join(input_folder, csv))
    sen_id = 0
    for filename in silver['filename'].unique():
        sentences = silver[silver['filename'] == filename]
        with open(os.path.join(text_folder, filename), "r", encoding="utf-8") as file:
            content = file.read()
            text_import = json_to_text(json_text=content)
        for index, row in sentences.iterrows():
            for span in text_import.new2_ner[row['from']:row['until']]:
                bio.loc[len(bio)] = [sen_id, span.text[0], span.nertag]
            sen_id += 1
    bio.to_csv(os.path.join(output_folder, csv), index=False)

if __name__ == '__main__':
    model_name = sys.argv[2]
    input_folder = 'data/silver_csv/' + model_name + '/pre_clean/'
    output_folder = 'data/silver_bio/' + model_name + '/pre_clean/'
    text_folder = 'data/first_model_tagged/' + model_name
    os.makedirs(output_folder, exist_ok=True)
    
    file_args = []

    start_time = time.time()

    for csv in os.listdir(input_folder):
        file_args.append((csv, input_folder, output_folder, text_folder))

    num_cores = int(sys.argv[3])
    print(f"Using {num_cores} CPU cores")

    with mp.Pool(processes=num_cores) as pool:
        results = pool.starmap(process, file_args)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Silver csv to bio ({csv}) - Elapsed time: {elapsed_time:.4f} seconds")