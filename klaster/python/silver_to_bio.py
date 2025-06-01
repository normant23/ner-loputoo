import estnltk
import os
import sys
import time
import pandas as pd
import multiprocessing as mp
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

def process_file(name, silver_subset, text_folder, start_sen_id):
    local_bio = pd.DataFrame(columns=['sentence_id', 'words', 'labels'])
    sen_id = start_sen_id
    
    with open(os.path.join(text_folder, name), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    
    for index, row in silver_subset.iterrows():
        for span in text_import.new2_ner[row['from']:row['until']]:
            local_bio.loc[len(local_bio)] = [sen_id, span.text[0], span.nertag]
        sen_id += 1
    
    return local_bio

def process_csv(csv, input_folder, output_folder, text_folder, num_cores):
    print(f"Processing {csv} with {num_cores} cores")
    silver = pd.read_csv(os.path.join(input_folder, csv))
    
    # Get unique filenames
    unique_files = silver['filename'].unique()
    
    # Create args for parallel processing
    file_args = []
    start_sen_id = 0
    
    for name in unique_files:
        silver_subset = silver[silver['filename'] == name]
        file_args.append((name, silver_subset, text_folder, start_sen_id))
        # Update the starting sentence ID for the next file
        start_sen_id += len(silver_subset)
    
    # Use multiprocessing to process files in parallel
    with mp.Pool(processes=num_cores) as pool:
        results = pool.starmap(process_file, file_args)
    
    # Combine results
    bio = pd.concat(results, ignore_index=True)
    
    # Save the final DataFrame
    bio.to_csv(os.path.join(output_folder, csv), index=False)
    
    return csv

if __name__ == '__main__':
    model_name = sys.argv[2]
    input_folder = f'data/silver_csv/{model_name}/clean/'
    output_folder = f'data/silver_bio/{model_name}/clean/'
    text_folder = f'data/first_model_tagged_clean/{model_name}'
    os.makedirs(output_folder, exist_ok=True)
    
    num_cores = int(sys.argv[3])
    print(f"Using {num_cores} CPU cores")
    
    start_time = time.time()
    
    # Get list of CSV files to process
    csv_files = os.listdir(input_folder)
    
    # OPTION 2: Process one CSV at a time with internal parallelism
    # This is the recommended approach to avoid the daemon process error
    for csv in csv_files:
        process_csv(csv, input_folder, output_folder, text_folder, num_cores)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Silver csv to bio conversion - Elapsed time: {elapsed_time:.4f} seconds")