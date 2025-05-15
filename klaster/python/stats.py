import os
import estnltk
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

input_folder = 'data/gold'

results = {}
unique = {}

for name in os.listdir(input_folder):
    with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)

    for ne in text_import.ne_gold_a:
        results[ne.tag] = results.get(ne.tag, 0) + 1
        if ne.tag not in unique:
            unique[ne.tag] = set()
        unique[ne.tag].add(ne.text)

print('-'*10)

unique_counts = {tag: len(values) for tag, values in unique.items()}

print(results)
print(unique_counts)

print()

input_folder = 'data/tudengid'

results = {}
unique = {}

for name in os.listdir(input_folder):
    with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)

    for ne in text_import.manual_named_entities:
        results[ne.tag[0]] = results.get(ne.tag[0], 0) + 1
        if ne.tag[0] not in unique:
            unique[ne.tag[0]] = set()
        unique[ne.tag[0]].add(ne.text)

unique_counts = {tag: len(values) for tag, values in unique.items()}

print(results)
print(unique_counts)