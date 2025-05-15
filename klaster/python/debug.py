import os
import time
import estnltk
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

inputs = ['data/koik', 'data/temp_sonestus_koik', 'data/gold', 'data/processed_gold', 'data/tudengid', 'data/temp_sonestus_tudengid']

start_time = time.time()

for input_folder in inputs:
    sen_count = 0
    word_count = 0

    for name in os.listdir(input_folder):
        with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
            content = file.read()
            text_import = json_to_text(json_text=content)

        sen_count += len(text_import.sentences)
        word_count += len(text_import.words)

    print(input_folder, sen_count, word_count)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Filter - Elapsed time: {elapsed_time:.4f} seconds")