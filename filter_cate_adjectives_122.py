import pandas as pd
import numpy as np
import re
import sys
from nltk.corpus import wordnet
import nltk

nltk.download('wordnet', quiet=True)

df_cate = pd.read_csv('data/derived_outputs/cate_words_full_224.csv')

# Explicit list of non-adjective verbs / action nouns to exclude
verbs_to_exclude = {
    'land', 'landed', 'visit', 'spent', 'pick', 'talk', 'giving', 'offer', 'received', 
    'eat', 'learn', 'knowing', 'capture', 'include', 'afford', 'agree', 'cooperate', 
    'learning', 'focus', 'skip', 'stress', 'join', 'joined', 'bother', 'docked', 
    'improved', 'reserve', 'soak', 'pull', 'granted', 'copy', 'lead', 'comprehend', 
    'hooked', 'noted', 'zip', 'building', 'payment', 'standing', 'traveling', 'reading',
    'rest', 'option', 'choice', 'reason', 'effort', 'breakfast', 'advantage', 'partner',
    'radio', 'march', 'culture', 'dinner', 'gear', 'degree', 'craft', 'prop', 'teens',
    'resident', 'fleet', 'flow', 'strut', 'lounge', 'model', 'wit', 'assistance', 'ruth',
    'phoenix', 'august', 'monument', 'pacific', 'prince', 'female', 'anchor'
}

filtered_rows = []

for idx, row in df_cate.iterrows():
    w_raw = str(row['CATE 词汇']).strip()
    m = re.match(r'^([a-zA-Z\-]+)', w_raw)
    if not m:
        continue
    w = m.group(1).lower()
    
    if w in verbs_to_exclude:
        continue
        
    filtered_rows.append(row)

df_filtered = pd.DataFrame(filtered_rows)

# Trim to top 122 adjectives / descriptive terms
df_122 = df_filtered.head(122).copy()

print(f"Filtered CATE Adjectives count: {len(df_122)}")
df_122.to_csv('data/derived_outputs/cate_words_adjectives_122.csv', index=False)
print("Saved 122 filtered CATE adjectives to data/derived_outputs/cate_words_adjectives_122.csv")

print("\nSample 122 CATE Adjectives:")
print(df_122[['CATE 词汇', '出现频次 (Freq)', '平均星级 (Stars)']].head(20).to_string(index=False))
