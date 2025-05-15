import os
import time
import sys
import torch
import estnltk
import pandas as pd

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text
from estnltk import download, get_resource_paths
#download("estbertner")
#from estnltk_neural.taggers import EstBERTNERTagger
from estbertner_tagger import EstBERTNERTagger
from nervaluate import Evaluator

def transform_data(layer, text):
    tags = {
        "PER": "PER",
        "LOC": "LOC",
        "LOC_ADDRESS": "LOC",
        "ORG": "ORG",
        "ORG_POL": "ORG",
        "ORG_GPE": "ORG",
    }

    data = []

    if layer == 'gold':
        for span in text.ne_gold_a:
            if span.tag in tags:
                data.append({"label": tags[span.tag], "start": span.start, "end": span.end})
    else:
        for span in text[layer]:
            data.append({"label": span.nertag, "start": span.start, "end": span.end})
    return data

def results(full_result, result_by_tags):
    result_str = f"Overall - precision:{round(full_result['strict']['precision'], 4)}, recall:{round(full_result['strict']['recall'], 4)}, f1:{round(full_result['strict']['f1'], 4)}\n"
    for tag, stats in result_by_tags.items():
        result_str += (tag + ':' + 
                ' precision: ' + str(round(stats['strict']['precision'], 4)) + ',' +
                ' recall: ' + str(round(stats['strict']['recall'], 4)) + ',' +
                ' f1: ' + str(round(stats['strict']['f1'], 4)) + '\n')
    #return result_str
    print(result_str)

input_folder = 'data/processed_gold'
#test_file = '1935-09-30_manual_annotated.json'

final_model_dir = sys.argv[2]
model_folder = f'final_model/{final_model_dir}/pre_clean/'
print(f'First model: {final_model_dir}')
test_files = []

batch_size = 1000
if final_model_dir == 'model_1932-01-25':
    batch_size = 750

for i in final_model_dir.split('_')[1:]:
    for j in os.listdir(input_folder):
        if j.startswith(i):
            test_files.append(j)
print(f'Test files: {test_files}, batch size: {batch_size}')

true = []
for test in test_files:
    with open(os.path.join(input_folder, test), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    true.append(transform_data('gold', text_import))

for model_name in sorted(os.listdir(model_folder)):
    checkpoint_dir = sorted(os.listdir(model_folder + model_name))[-1]
    model = EstBERTNERTagger(model_location=model_folder + model_name + '/' + checkpoint_dir, output_layer='new_final_ner', batch_size=batch_size)
    finalner = []
    for test in test_files:
        with open(os.path.join(input_folder, test), "r", encoding="utf-8") as file:
            content = file.read()
            text_import = json_to_text(json_text=content)
        model.tag(text_import)
        finalner.append(transform_data('new_final_ner', text_import))
    finalner_eval = Evaluator(true, finalner, tags=['LOC', 'ORG', 'PER'])
    results2, results_per_tag2, result_indices2, result_indices_by_tag2 = finalner_eval.evaluate()
    print(model_name)
    results(results2, results_per_tag2)

#estbertner
estbert_ner = EstBERTNERTagger(batch_size=batch_size)
estbertner = []
for test in test_files:
    with open(os.path.join(input_folder, test), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    estbert_ner.tag(text_import)
    estbertner.append(transform_data('estbertner', text_import))
estbertner_eval = Evaluator(true, estbertner, tags=['LOC', 'ORG', 'PER'])
results1, results_per_tag1, result_indices1, result_indices_by_tag1 = estbertner_eval.evaluate()
print('estbertner')
results(results1, results_per_tag1)

#opetaja - first model
checkpoint_dir = sorted(os.listdir('first_model/' + final_model_dir))[-1]
new2_ner = EstBERTNERTagger(model_location='first_model/' + final_model_dir + '/' + checkpoint_dir, output_layer='new2_ner', batch_size=batch_size)
new2 = []
for test in test_files:
    with open(os.path.join(input_folder, test), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    new2_ner.tag(text_import)
    new2.append(transform_data('new2_ner', text_import))
new2_eval = Evaluator(true, new2, tags=['LOC', 'ORG', 'PER'])
results1, results_per_tag1, result_indices1, result_indices_by_tag1 = new2_eval.evaluate()
print('opetaja - first model')
results(results1, results_per_tag1)

#tudeng
checkpoint_dir = sorted(os.listdir('final_model/model_tudeng'))[-1]
new2_ner = EstBERTNERTagger(model_location='final_model/model_tudeng/' + checkpoint_dir, output_layer='new2_ner', batch_size=batch_size)
new2 = []
for test in test_files:
    with open(os.path.join(input_folder, test), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    new2_ner.tag(text_import)
    new2.append(transform_data('new2_ner', text_import))
new2_eval = Evaluator(true, new2, tags=['LOC', 'ORG', 'PER'])
results1, results_per_tag1, result_indices1, result_indices_by_tag1 = new2_eval.evaluate()
print('tudeng')
results(results1, results_per_tag1)

#tudeng fixed
checkpoint_dir = sorted(os.listdir('final_model/model_tudeng_fixed'))[-1]
new2_ner = EstBERTNERTagger(model_location='final_model/model_tudeng_fixed/' + checkpoint_dir, output_layer='new2_ner', batch_size=batch_size)
new2 = []
for test in test_files:
    with open(os.path.join(input_folder, test), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    new2_ner.tag(text_import)
    new2.append(transform_data('new2_ner', text_import))
new2_eval = Evaluator(true, new2, tags=['LOC', 'ORG', 'PER'])
results1, results_per_tag1, result_indices1, result_indices_by_tag1 = new2_eval.evaluate()
print('tudeng')
results(results1, results_per_tag1)