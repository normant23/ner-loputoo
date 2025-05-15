import estnltk
import os
import sys
import time
import pandas as pd

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

from nervaluate import Evaluator
from estnltk_neural.taggers import EstBERTNERTagger
from new2_ner_tagger import New2NerTagger
from estnltk import download, get_resource_paths

input_folder = 'data/processed_gold'

groups = [['1922-04-24_manual_annotated.json', '1936-09-07_manual_annotated.json'], 
          ['1927-03-28_manual_annotated.json', '1941-01-03_manual_annotated.json'], 
          ['1932-01-25_manual_annotated.json'], 
          ['1934-10-15_manual_annotated.json'], 
          ['1935-09-30_manual_annotated.json']]

tags = {
    "PER": "PER",
    "LOC": "LOC",
    "LOC_ADDRESS": "LOC",
    "ORG": "ORG",
    "ORG_POL": "ORG",
    "ORG_GPE": "ORG",
}

for group in groups:
    tag_counts = {
        "PER": 0,
        "LOC": 0,
        "ORG": 0,
    }
    words = 0
    sens = 0
    name = []
    
    for filename in group:
        name.append(filename.split('_')[0])
        with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as file:
            content = file.read()
            text_import = json_to_text(json_text=content)

        sens += len(text_import.sentences)
        words += len(text_import.words)

        for tag in text_import.ne_gold_a:
            if tag.tag in tags.keys():
                tag_counts[tags[tag.tag]] += 1
    
    print(name)
    print(words, sens)
    print(tag_counts)
    print(tag_counts['PER'] + tag_counts['LOC'] + tag_counts['ORG'])
    print()
