import pandas as pd
import numpy as np
import re
import os

master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
print(f"Loading master dataset from {master_path}...")
df = pd.read_csv(master_path)
total_n = len(df)

safety_words = [
    'safe', 'safety', 'smooth', 'professional', 'comfortable',
    'relax', 'reassured', 'reassuring', 'comfort', 'good hands',
    'trust', 'calm', 'confidence', 'confident', 'ease',
    'expert', 'capable', 'secure', 'reassurance', 'gentle',
    'security', 'flawless', 'trusted'
]

results = []

for word in safety_words:
    pattern = r'\b' + re.escape(word) + r'\b'
    matches = df['review_text'].fillna('').str.contains(pattern, case=False, regex=True)
    count = matches.sum()
    pct = round(count / total_n * 100, 2)
    
    # Extract 2 representative sentence examples
    matching_texts = df[matches]['review_text'].tolist()
    sample_sents = []
    for txt in matching_texts:
        sents = [s.strip() for s in re.split(r'[.!?;\n]+', str(txt)) if re.search(pattern, s, re.I)]
        for s in sents:
            if len(s) < 120 and len(s) > 15:
                sample_sents.append(s)
                break
        if len(sample_sents) >= 2:
            break
            
    ex1 = sample_sents[0] if len(sample_sents) > 0 else ""
    ex2 = sample_sents[1] if len(sample_sents) > 1 else ""
    
    results.append({
        'safety_word': word,
        'count': count,
        'percentage': pct,
        'example_1': ex1,
        'example_2': ex2
    })

res_df = pd.DataFrame(results).sort_values(by='count', ascending=False)
out_csv = 'data/derived_outputs/safety_words_frequency_analysis.csv'
res_df.to_csv(out_csv, index=False, encoding='utf-8-sig')
print(f"\nSaved Safety Words Frequency Analysis -> {out_csv}")
print("\nTop 15 Most Frequent Safety Words:")
print(res_df[['safety_word', 'count', 'percentage']].head(15).to_string(index=False))
