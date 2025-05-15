import os
import time
import sys
import torch
import estnltk
import pandas as pd
import multiprocessing as mp
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

def results(full_result, result_by_tags):
    result_str = f"Overall - precision:{round(full_result['strict']['precision'], 4)}, recall:{round(full_result['strict']['recall'], 4)}, f1:{round(full_result['strict']['f1'], 4)}\n"
    for tag, stats in result_by_tags.items():
        result_str += (tag + ':' + 
                ' precision: ' + str(round(stats['strict']['precision'], 4)) + ',' +
                ' recall: ' + str(round(stats['strict']['recall'], 4)) + ',' +
                ' f1: ' + str(round(stats['strict']['f1'], 4)) + '\n')
    return result_str

def process_model(model_info):
    model_name, model_path, content = model_info
    
    try:
        # Create new text object from content for thread safety
        text_import = json_to_text(json_text=content)
        true = transform_data('gold', text_import)
        
        model = EstBERTNERTagger(model_location=model_path, 
                                output_layer='new_final_ner', 
                                batch_size=1000, device=torch.device)
        model.tag(text_import)
        
        finalner = transform_data('new_final_ner', text_import)
        finalner_eval = Evaluator(true, finalner, tags=['LOC', 'ORG', 'PER'])
        results2, results_per_tag2, _, _ = finalner_eval.evaluate()
        
        return model_name, results2, results_per_tag2
    except Exception as e:
        return model_name, f"Error processing {model_name}: {str(e)}"

if __name__ == "__main__":
    start_time = time.time()
    
    input_folder = 'data/processed_gold'
    test_file = '1935-09-30_manual_annotated.json'
    
    with open(os.path.join(input_folder, test_file), "r", encoding="utf-8") as file:
        content = file.read()
    
    # Prepare list of models to process
    models_to_process = []
    print("extra_pre_clean")
    for model_name in sorted(os.listdir('final_model/extra_pre_clean/')):
        model_dir = sorted(os.listdir('final_model/extra_pre_clean/' + model_name))[-1]
        model_path = 'final_model/extra_pre_clean/' + model_name + '/' + model_dir
        models_to_process.append((model_name, model_path, content))
    
    # Use multiprocessing to process models in parallel
    num_cores = int(sys.argv[2])
    print(f"Using {num_cores} CPU cores")
    
    with mp.Pool(processes=num_cores) as pool:
        results_list = pool.map(process_model, models_to_process)
    
    # Print results
    for model_name, full_result, result_by_tags in results_list:
        print(f"\n{model_name}")
        print(results(full_result, result_by_tags))

    
    # Process estbertner and opetaja separately or add them to the pool as well
    text_import = json_to_text(json_text=content)
    true = transform_data('gold', text_import)
    
    print("\nestbertner")
    estbert_ner = EstBERTNERTagger(batch_size=1000, device=torch.device)
    estbert_ner.tag(text_import)
    estbertner = transform_data('estbertner', text_import)
    estbertner_eval = Evaluator(true, estbertner, tags=['LOC', 'ORG', 'PER'])
    results1, results_per_tag1, _, _ = estbertner_eval.evaluate()
    print(results(results1, results_per_tag1))
    
    print("\nopetaja")
    new2_ner = EstBERTNERTagger(model_location='model/best_model3', output_layer='new2_ner', batch_size=1000, device=torch.device)
    new2_ner.tag(text_import)
    new2 = transform_data('new2_ner', text_import)
    new2_eval = Evaluator(true, new2, tags=['LOC', 'ORG', 'PER'])
    results1, results_per_tag1, _, _ = new2_eval.evaluate()
    print(results(results1, results_per_tag1))
    
    print(f"\nTotal execution time: {time.time() - start_time:.2f} seconds")