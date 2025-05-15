import os
import time
import estnltk
import pandas as pd
from estnltk import Text
from estnltk.converters import text_to_json, json_to_text

def find_sentence(text, index):
    for sen in text.sentences:
        if sen.start <= idnex and sen.end > index:
            return sen

input_folder = 'data/tagged_koik'
sen_df = pd.read_csv('data/tagged_sen_csv/70.csv')

for name in list(sen_df['filename'].unique()):
    print(name)
    with open(os.path.join(input_folder, name), "r", encoding="utf-8") as file:
        content = file.read()
        text_import = json_to_text(json_text=content)
    sentences = sen_df[sen_df['filename'] == name]
    current = ''
    for index, row in sentences.iterrows():
        for span in text_import.new2_ner[row['from']:row['until']]:
            if span.nertag == 'O':
                current = 'O'
            elif span.nertag.startswith('B-'):
                current = span.nertag[-3:]
            elif span.nertag.startswith('I-'):
                if current != span.nertag[-3:]:
                    print(span.start, span.nertag, span.text, span.prob)
                    print(text_import.new2_ner[row['from']:row['until']].text)
                    print(text_import.new2_ner[row['from']:row['until']].nertag)
    print()