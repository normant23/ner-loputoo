import os

input_folder = 'data/silver_bio'
total = 0

for model in os.listdir('first_model'):
    all_files = os.listdir(f'{input_folder}/{model}/pre_clean')
    total += len([file for file in all_files if file.split('_')[0].endswith('00')])

print(total)