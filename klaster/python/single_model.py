import estnltk
import os
import sys
import time

import pandas as pd
import numpy as np

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text
from estnltk_core.layer.span_operations import conflict

import logging
from simpletransformers.ner import NERModel, NERArgs

def split_data(df):
    np.random.seed(42)
    unique_sentences = df['sentence_id'].unique()
    np.random.shuffle(unique_sentences)
    split_idx = int(len(unique_sentences) * 0.8)
    train_sentences = unique_sentences[:split_idx]
    test_sentences = unique_sentences[split_idx:]
    train_df = df[df['sentence_id'].isin(train_sentences)]
    test_df = df[df['sentence_id'].isin(test_sentences)]
    return train_df, test_df

start_time = time.time()

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)

labels = ['O', 'B-PER', 'I-PER', 'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC']

input_path = sys.argv[2]
output_folder = 'final_model/model_tudeng_fixed_new'
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv(input_path)
df = df.astype(str)
train_df, test_df = split_data(df)

#model_name = "model" + csv[:-4]
#os.makedirs("final_model/clean/" + model_name, exist_ok=True)
model_args = NERArgs()
model_args.train_batch_size = 16
model_args.evaluate_during_training = True
model_args.overwrite_output_dir = True
model = NERModel(
    "bert", "tartuNLP/EstBERT_NER", args=model_args, labels=labels, use_cuda=True
)

model.train_model(train_data=train_df, eval_data=test_df, output_dir=output_folder)
result, model_outputs, preds_list = model.eval_model(test_df)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Model 2 training time ({input_path}): {elapsed_time:.4f} seconds")