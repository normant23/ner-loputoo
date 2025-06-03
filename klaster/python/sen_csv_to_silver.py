import estnltk
import os
import sys
import time
import pandas as pd
import multiprocessing as mp

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

def get_selected(df, target_sum):
    selected_rows = pd.DataFrame(columns=df.columns)
    current_sum = 0
    for i, row in df.iterrows():
        if current_sum <= target_sum:
            selected_rows = pd.concat([selected_rows, pd.DataFrame([row])], ignore_index=True)
            current_sum += row['total_counts']
        else:
            break
    return selected_rows

def process(csv, input_folder, output_folder):
    sen_df = pd.read_csv(os.path.join(input_folder, csv))
    sen_df['total_counts'] = sen_df['loc_count'] + sen_df['per_count'] + sen_df['org_count']
    shuffled_df = sen_df.sample(frac=1, random_state=42).reset_index(drop=True)
    total_tags = shuffled_df['total_counts'].sum()
    step = 6500
    while step < total_tags:
        selected = get_selected(shuffled_df, step)
        name = str(step) + '_' + csv
        selected.to_csv(os.path.join(output_folder, name), index=False)
        step += 6500
    print(csv, total_tags, step, step - 3250)
    if total_tags > step - 3250 or total_tags < 6500:
        name = str(total_tags) + '_' + csv
        shuffled_df.to_csv(os.path.join(output_folder, name), index=False)

if __name__ == '__main__':
    model_name = sys.argv[2]
    input_folder = f'data/tagged_sen_csv/{model_name}/pre_clean'
    output_folder = f'data/silver_csv/{model_name}/pre_clean'
    os.makedirs(output_folder, exist_ok=True)
    
    file_args = []

    start_time = time.time()

    for csv in os.listdir(input_folder):
        file_args.append((csv, input_folder, output_folder))

    num_cores = int(sys.argv[3])
    print(f"Using {num_cores} CPU cores")

    with mp.Pool(processes=num_cores) as pool:
        results = pool.starmap(process, file_args)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Tagged sentences csv to silver csv (files:{len(os.listdir(input_folder))}) - Elapsed time: {elapsed_time:.4f} seconds")
