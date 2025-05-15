import os
import time
import estnltk
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text
from new2_ner_tagger import New2NerTagger

input_folder = 'data/uus_koik'
output_folder = 'data/temp'
new2_ner = New2NerTagger(model_location='model/best_model', output_layer='new2_ner', batch_size=850)

for name in os.listdir(input_folder)[:5]:
    with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
        content = file.read()
    text_import = json_to_text(json_text=content)
    new2_ner.tag(text_import)
    text_to_json(text_import, file=(output_folder + "/" + name))

with open(os.path.join(output_folder, os.listdir(output_folder)[0]), "r", encoding="utf-8") as file:
    content = file.read()
text_import = json_to_text(json_text=content)
print(text_import.new2_ner[:10])