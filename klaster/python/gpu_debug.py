import os
import time
import torch
import estnltk
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

from new2_ner_tagger import New2NerTagger

input_folder = 'data/processed_gold'
test_file = '1935-09-30_manual_annotated.json'

for model_name in sorted(os.listdir('first_model/')):
    with open(os.path.join(input_folder, test_file), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)

    print(torch.cuda.is_available())  # Should return True
    #print(torch.cuda.device_count())  # Number of GPUs available
    #print(torch.cuda.get_device_name(0))  # Name of the first GPU

    model_dir = sorted(os.listdir('first_model/' + model_name))[-1]
    model_path = 'first_model/' + model_name + '/' + model_dir
    #output_folder = 'data/first_model_tagged/' + model_name
    #os.makedirs(output_folder, exist_ok=True)
    new2_ner = New2NerTagger(model_location=model_path, output_layer='new2_ner', batch_size=700)

    print(text_import.layers)
    start_time = time.time()
    new2_ner.tag(text_import)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(text_import.layers)
    print(f"Elapsed time: {elapsed_time:.4f} seconds")

    print(text_import.new2_ner[0].text, text_import.new2_ner[0].prob, text_import.new2_ner[0].nertag)

    break