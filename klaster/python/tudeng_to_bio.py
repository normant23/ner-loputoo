import estnltk
import os
import sys
import time
import pandas as pd
import multiprocessing as mp

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text
from estnltk_core.layer.span_operations import conflict

def next_tag(text_import, tagnr):
    tags = {
        "person": "PER",
        "place": "LOC",
        "Address": "LOC",
        "organization": "ORG",
        "party": "ORG",
    }
    
    tagnr += 1
    
    while True:
        if tagnr >= len(text_import.manual_named_entities):
            return -1
        if text_import.manual_named_entities[tagnr].tag[0] in tags:
            return tagnr
        else:
            tagnr += 1

def process_file(file_name, directory):
    with open(os.path.join(directory, file_name), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    
    data = []
    tag_nr = next_tag(text_import, -1)
    sen_nr = 0
    
    tags = {
        "person": "PER",
        "place": "LOC",
        "Address": "LOC",
        "organization": "ORG",
        "party": "ORG",
    }

    # Process each word
    for word in text_import.words:
        # Update sentence ID if needed
        if sen_nr < len(text_import.sentences) and not conflict(text_import.sentences[sen_nr], word):
            sen_nr += 1

        if tag_nr != -1:
            tag = text_import.manual_named_entities[tag_nr]
            
            # If word is before the current entity
            if word.end <= tag.start:
                # Add as regular word
                data.append([file_name, sen_nr, word.text, "O"])

            elif word.start == tag.start:
                normalized_tag = tags.get(tag.tag[0], tag.tag[0])
                data.append([file_name, sen_nr, word.text, f"B-{normalized_tag}"])
            # If word is part of the current entity
            elif conflict(tag, word):
                normalized_tag = tags.get(tag.tag[0], tag.tag[0])
                data.append([file_name, sen_nr, word.text, f"I-{normalized_tag}"])
                
            # If word is after the current entity
            elif word.start >= tag.end:
                tag_nr = next_tag(text_import, tag_nr)
                
                if tag_nr != -1:
                    tag = text_import.manual_named_entities[tag_nr]

                    if word.start == tag.start:
                        normalized_tag = tags.get(tag.tag[0], tag.tag[0])
                        data.append([file_name, sen_nr, word.text, f"B-{normalized_tag}"])
                    else:
                        data.append([file_name, sen_nr, word.text, "O"])
                else:
                    data.append([file_name, sen_nr, word.text, "O"])
        else:
            data.append([file_name, sen_nr, word.text, "O"])
    
    return data

def filter_sentences(df, min_words=5):
    # Group by filename and sentence_id
    grouped = df.groupby(['filename', 'sentence_id'])
    
    # Keep valid sentences that meet both criteria
    valid_sentences = []
    for (filename, sent_id), group in grouped:
        # Check if sentence has at least one non-O label
        has_entities = not all(label == 'O' for label in group['labels'])
        
        # Check if sentence has enough words
        has_enough_words = len(group) >= min_words
        
        # Only keep sentences that satisfy both conditions
        if has_entities and has_enough_words:
            valid_sentences.append((filename, sent_id))
    
    # Filter the DataFrame to only keep valid sentences
    if valid_sentences:
        # Create a set for faster lookups
        valid_set = set(valid_sentences)
        mask = df.apply(lambda row: (row['filename'], row['sentence_id']) in valid_set, axis=1)
        filtered_df = df[mask].copy()
        
        # Create a mapping from (filename, sentence_id) to new unique ID
        unique_combinations = filtered_df[['filename', 'sentence_id']].drop_duplicates().reset_index(drop=True)
        id_mapping = {(row['filename'], row['sentence_id']): idx 
                     for idx, row in unique_combinations.iterrows()}
        
        # Apply the mapping to create a new sentence_id column
        filtered_df['new_sentence_id'] = filtered_df.apply(
            lambda row: id_mapping[(row['filename'], row['sentence_id'])], 
            axis=1
        )
        
        # Drop original filename and sentence_id columns, rename new_sentence_id to sentence_id
        filtered_df = filtered_df.drop(['filename', 'sentence_id'], axis=1)
        filtered_df = filtered_df.rename(columns={'new_sentence_id': 'sentence_id'})
        
        return filtered_df
    else:
        # Return empty DataFrame with correct columns
        return df.drop(['filename'], axis=1).iloc[0:0]

if __name__ == '__main__':
    input_folder = 'data/processed_tudengid/'
    output_folder= 'data/tudeng_bio_new/'
    os.makedirs(output_folder, exist_ok=True)

    file_args = []
    start_sen_id = 0
    start_time = time.time()

    for name in os.listdir(input_folder):
        file_args.append((name, input_folder))

    num_cores = int(sys.argv[2])
    print(f"Using {num_cores} CPU cores")
    
    with mp.Pool(processes=num_cores) as pool:
        results = pool.starmap(process_file, file_args)

    all_data = []
    for result in results:
        all_data.extend(result)
    
    data = pd.DataFrame(all_data, columns=["filename", "sentence_id", "words", "labels"])

    data = filter_sentences(data)

    data.to_csv(output_folder + 'filtered_tudeng_bio.csv', index=False)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Tudeng to csv (number of csv: {len(os.listdir(input_folder))}) - Elapsed time: {elapsed_time:.4f} seconds")