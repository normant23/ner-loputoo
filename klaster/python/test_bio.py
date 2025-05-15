import estnltk
import os
import sys
import time
import pandas as pd
import multiprocessing as mp
from functools import partial
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

def process_file(name, silver_subset, input_folder, start_sen_id):
    local_bio = pd.DataFrame(columns=['sentence_id', 'words', 'labels'])
    sen_id = start_sen_id
    
    with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    
    for index, row in silver_subset.iterrows():
        for span in text_import.new2_ner[row['from']:row['until']]:
            local_bio.loc[len(local_bio)] = [sen_id, span.text[0], span.nertag]
        sen_id += 1
    
    return local_bio

if __name__ == '__main__':
    start_time = time.time()
    csv = sys.argv[2]
    silver = pd.read_csv('data/silver_csv/extra_pre_clean/' + csv)
    input_folder = 'data/tagged_koik'
    
    # Get unique filenames
    unique_files = silver['filename'].unique()
    
    # Create args for parallel processing
    file_args = []
    start_sen_id = 0
    
    for name in unique_files:
        silver_subset = silver[silver['filename'] == name]
        file_args.append((name, silver_subset, input_folder, start_sen_id))
        # Update the starting sentence ID for the next file
        start_sen_id += len(silver_subset)
    
    # Use multiprocessing to process files in parallel
    #num_cores = mp.cpu_count()
    num_cores = int(sys.argv[3])
    print(f"Using {num_cores} CPU cores")
    
    with mp.Pool(processes=num_cores) as pool:
        results = pool.starmap(process_file, file_args)
    
    # Combine results
    bio = pd.concat(results, ignore_index=True)
    
    # Save the final DataFrame
    bio.to_csv('data/silver_bio/extra_pre_clean/' + csv, index=False)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Silver csv to bio ({csv}, cores:{num_cores}) - Elapsed time: {elapsed_time:.4f} seconds")