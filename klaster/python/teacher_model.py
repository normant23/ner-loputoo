import estnltk
import os
import time

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

from estnltk_core.layer.span_operations import conflict
import pandas as pd

import logging
from simpletransformers.ner import NERModel, NERArgs

def next_tag(text_import, tagnr):
    tags = {
        "PER": "PER",
        "LOC": "LOC",
        "LOC_ADDRESS": "LOC",
        "ORG": "ORG",
        "ORG_POL": "ORG",
        "ORG_GPE": "ORG",
    }
    
    tagnr += 1
    
    while True:
        if tagnr >= len(text_import.ne_gold_a):
            return -1
        if text_import.ne_gold_a[tagnr].tag in tags:
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
        "PER": "PER",
        "LOC": "LOC",
        "LOC_ADDRESS": "LOC",
        "ORG": "ORG",
        "ORG_POL": "ORG",
        "ORG_GPE": "ORG",
    }

    # Process each word
    for word in text_import.words:
        # Update sentence ID if needed
        if sen_nr < len(text_import.sentences) and not conflict(text_import.sentences[sen_nr], word):
            sen_nr += 1

        if tag_nr != -1:
            tag = text_import.ne_gold_a[tag_nr]
            
            # If word is before the current entity
            if word.end <= tag.start:
                # Add as regular word
                data.append([file_name, sen_nr, word.text, "O"])

            elif word.start == tag.start:
                normalized_tag = tags.get(tag.tag, tag.tag)
                data.append([file_name, sen_nr, word.text, f"B-{normalized_tag}"])
            # If word is part of the current entity
            elif conflict(tag, word):
                normalized_tag = tags.get(tag.tag, tag.tag)
                data.append([file_name, sen_nr, word.text, f"I-{normalized_tag}"])
                
            # If word is after the current entity
            elif word.start >= tag.end:
                tag_nr = next_tag(text_import, tag_nr)
                
                if tag_nr != -1:
                    tag = text_import.ne_gold_a[tag_nr]

                    if word.start == tag.start:
                        normalized_tag = tags.get(tag.tag, tag.tag)
                        data.append([file_name, sen_nr, word.text, f"B-{normalized_tag}"])
                    else:
                        data.append([file_name, sen_nr, word.text, "O"])
                else:
                    data.append([file_name, sen_nr, word.text, "O"])
        else:
            data.append([file_name, sen_nr, word.text, "O"])
    
    return data

def process_directory_to_dict(dir):
    all_data = []
    
    for name in os.listdir(dir):
        all_data.extend(process_file(name, dir))

    data = pd.DataFrame(all_data, columns=["filename", "sentence_id", "words", "labels"])
    return data

def getData(data, group):
    group_data = data[data['filename'].isin(group)].copy()
    if len(group) == 1:
        return group_data
    group_data = group_data.sort_values(by=['filename', 'sentence_id'])
    current_max_id = 0
    for file in group:
        group_data.loc[group_data['filename'] == file, 'sentence_id'] += current_max_id
        current_max_id = group_data[group_data['filename'] == file]['sentence_id'].max() + 1
    group_data.drop('filename', axis=1, inplace=True)
    return group_data

groups = [['1922-04-24_manual_annotated.json', '1936-09-07_manual_annotated.json'], 
          ['1927-03-28_manual_annotated.json', '1941-01-03_manual_annotated.json'], 
          ['1932-01-25_manual_annotated.json'], 
          ['1934-10-15_manual_annotated.json'], 
          ['1935-09-30_manual_annotated.json']]

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)

labels = ['O', 'B-PER', 'I-PER', 'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC']

data = process_directory_to_dict('data/processed_gold')
start_time = time.time()

for eval_nr, eval_group in enumerate(groups):
    model_name = "model_" + "_".join(element[:10] for element in eval_group)
    print(eval_group)
    os.makedirs("first_model/" + model_name, exist_ok=True)
    model_args = NERArgs()
    model_args.train_batch_size = 16
    model_args.evaluate_during_training = True
    model_args.overwrite_output_dir = True
    model = NERModel(
        "bert", "tartuNLP/EstBERT", args=model_args, labels=labels, use_cuda=True
    )
    eval_data = getData(data, eval_group)
    
    all_train_files = []
    for i, group in enumerate(groups):
        if i != eval_nr:  # Skip the evaluation group
            all_train_files.extend(group)
    
    train_data = getData(data, all_train_files)
    model.train_model(train_data=train_data, eval_data=eval_data, output_dir="first_model/" + model_name)
    result, model_outputs, preds_list = model.eval_model(eval_data)
    print(result)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")