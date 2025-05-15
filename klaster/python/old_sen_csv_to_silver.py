import estnltk
import os
import time
import pandas as pd

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

start_time = time.time()

def get_selected(df, target_sum):
    selected_rows = pd.DataFrame(columns=df.columns)
    current_sum = 0
    for i, row in shuffled_df.iterrows():
        if current_sum <= target_sum:
            selected_rows = pd.concat([selected_rows, pd.DataFrame([row])], ignore_index=True)
            current_sum += row['total_counts']
        else:
            break
    return selected_rows

for csv in os.listdir('data/tagged_sen_csv/clean'):
    sen_df = pd.read_csv('data/tagged_sen_csv/clean/' + csv)
    sen_df_o = pd.read_csv('data/tagged_sen_csv/clean_o/O_90.csv')
    sen_df = pd.concat([sen_df, sen_df_o], axis=0)
    sen_df['total_counts'] = sen_df['loc_count'] + sen_df['per_count'] + sen_df['org_count']
    shuffled_df = sen_df.sample(frac=1, random_state=42).reset_index(drop=True)
    total_tags = shuffled_df['total_counts'].sum()
    step = 6500
    while step < total_tags:
        selected = get_selected(shuffled_df, step)
        name = str(step) + '_' + csv
        selected.to_csv('data/silver_csv/clean/' + name, index=False)
        step += 6500
    print(csv, total_tags, step, step - 3250), 
    if total_tags > step - 3250 or total_tags < 6500:
        name = str(total_tags) + '_' + csv
        shuffled_df.to_csv('data/silver_csv/clean/' + name, index=False)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Tagged sentences csv to silver csv (files:{len(os.listdir('data/tagged_sen_csv/clean'))}) - Elapsed time: {elapsed_time:.4f} seconds")
