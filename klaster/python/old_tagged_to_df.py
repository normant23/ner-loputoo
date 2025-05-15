import estnltk
import os
import time
import pandas as pd
import multiprocessing as mp

from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

model_name = sys.argv[2]
cores = int(sys.argv[3])
input_folder = 'data/first_model_tagged/' + model_name
os.makedirs('data/tagged_sen_csv/' + model_name, exist_ok=True)
os.makedirs('data/tagged_sen_csv/' + model_name + '/' + 'pre_clean', exist_ok=True)
prob_limits = [0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
#prob_limits = [0.8, 0.85, 0.9]

start_time = time.time()

for limit in prob_limits:
    df = pd.DataFrame(columns=['filename', 'sen_nr', 'from', 'until', 'loc_count', 'per_count', 'org_count'])
    for name in os.listdir(input_folder):
        with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
            content = file.read()
            text_import = json_to_text(json_text=content)
        
        last_index = 0
        
        for sen_nr, sen in enumerate(text_import.sentences):
            counts = {
                'B-LOC': 0,
                'B-PER': 0,
                'B-ORG': 0
            }
            add_sen_prob = True
            for span in text_import.new2_ner[last_index:(last_index + len(sen.text))]:
                if span.prob < limit:
                    add_sen_prob = False
                    break
                if span.nertag in counts:
                    counts[span.nertag] += 1
            #if add_sen_prob and len(sen.text) > 4 and counts['B-LOC'] + counts['B-PER'] + counts['B-ORG'] == 0:
            if add_sen_prob and len(sen.text) > 4:
                df.loc[len(df)] = (name, sen_nr, last_index, last_index + len(sen.text), counts['B-LOC'], counts['B-PER'], counts['B-ORG'])
            last_index += len(sen.text)

    print()
    print("Limit:", limit)
    print(len(df))
    print("files", len(df['filename'].unique()))
    print("loc", df['loc_count'].sum(),"per", df['per_count'].sum(), "org", df['org_count'].sum())
    df.to_csv(f'data/tagged_sen_csv/{model_name}/pre_clean/{int(limit*100)}.csv', index=False)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Tagged to csv (different prob limits: {len(prob_limits)}) - Elapsed time: {elapsed_time:.4f} seconds")