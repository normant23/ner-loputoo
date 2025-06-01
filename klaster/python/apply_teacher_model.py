import os
import time
import torch
import estnltk
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

from new2_ner_tagger import New2NerTagger

input_folder = 'data/uus_koik'

start_time = time.time()

for model_name in sorted(os.listdir('first_model/')):
    print(torch.device)
    model_dir = sorted(os.listdir('first_model/' + model_name))[-1]
    model_path = 'first_model/' + model_name + '/' + model_dir
    output_folder = 'data/first_model_tagged/' + model_name
    os.makedirs(output_folder, exist_ok=True)
    new2_ner = New2NerTagger(model_location=model_path, output_layer='new2_ner', batch_size=700)

    for name in os.listdir(input_folder):
        with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
            content = file.read()
            text_import = json_to_text(json_text=content)

        new2_ner.tag(text_import)
        text_to_json(text_import, file=(output_folder + "/" + name))

end_time = time.time()
elapsed_time = end_time - start_time
print(f"New NER2 (num of mdoels {len(os.listdir('first_model/'))}) - Elapsed time: {elapsed_time:.4f} seconds")
