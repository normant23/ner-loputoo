import estnltk
import os
import time

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

from estnltk import download, get_resource_paths
download("estbertner")

from estnltk_neural.taggers import EstBERTNERTagger

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
    return [data]

def results(data):
    for tag, stats in data.items():
        print(tag + ':', 
              'precision:', str(round(stats['strict']['precision'], 4)) + ',', 
              'recall:', str(round(stats['strict']['recall'], 4)) + ',',
              'f1:', str(round(stats['strict']['f1'], 4)))

input_folder = 'data/processed_gold'
test_file = '1935-09-30_manual_annotated.json'

with open(os.path.join(input_folder, test_file), "r", encoding="utf-8") as file:
    content = file.read()
    text_import = json_to_text(json_text=content)

true = transform_data('gold', text_import)

for model_name in sorted(os.listdir('final_model/pre_clean/')):
    model_dir = sorted(os.listdir('final_model/pre_clean/' + model_name))[-1]
    model = EstBERTNERTagger(model_location='final_model/pre_clean/' + model_name + '/' + model_dir, output_layer='new_final_ner', batch_size=1000)
    model.tag(text_import)
    finalner = transform_data('new_final_ner', text_import)
    finalner_eval = Evaluator(true, finalner, tags=['LOC', 'ORG', 'PER'])
    results2, results_per_tag2, result_indices2, result_indices_by_tag2 = finalner_eval.evaluate()
    print()
    print(model_name)
    results(results_per_tag2)
    text_import.pop_layer('new_final_ner')

#estbertner
estbert_ner = EstBERTNERTagger(batch_size=1000)
estbert_ner.tag(text_import)
estbertner = transform_data('estbertner', text_import)
estbertner_eval = Evaluator(true, estbertner, tags=['LOC', 'ORG', 'PER'])
results1, results_per_tag1, result_indices1, result_indices_by_tag1 = estbertner_eval.evaluate()
print()
print('estbertner')
results(results_per_tag1)

#opetaja
new2_ner = EstBERTNERTagger(model_location='model/best_model3', output_layer='new2_ner', batch_size=1000)
new2_ner.tag(text_import)
new2 = transform_data('new2_ner', text_import)
new2_eval = Evaluator(true, new2, tags=['LOC', 'ORG', 'PER'])
results1, results_per_tag1, result_indices1, result_indices_by_tag1 = new2_eval.evaluate()
print()
print('opetaja')
results(results_per_tag1)