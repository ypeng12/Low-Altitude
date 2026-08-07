import pandas as pd
import numpy as np
import os
import sys
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np

# Patch numpy 2.0 copy=False deprecation for fasttext-wheel
_orig_np_array = np.array
def _patched_np_array(obj, *args, **kwargs):
    if kwargs.get('copy') is False:
        kwargs.pop('copy')
    return _orig_np_array(obj, *args, **kwargs)
np.array = _patched_np_array

import fasttext
from langdetect import detect_langs, DetectorFactory

DetectorFactory.seed = 42
sys.stdout.reconfigure(encoding='utf-8')

sia = SentimentIntensityAnalyzer()

model_path = 'lid.176.bin'
print(f"Loading FastText model from {model_path}...")
ft_model = fasttext.load_model(model_path)

master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
print(f"Loading master dataset from {master_path}...")
df = pd.read_csv(master_path)
print(f"Total Master Rows: {len(df)}")

def clean_text_for_fasttext(text):
    if not isinstance(text, str):
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text.strip()

texts = (df['review_title'].fillna('') + ' ' + df['review_text'].fillna('')).apply(clean_text_for_fasttext).tolist()

print("\nRunning FastText Language Identification (LID) across all reviews...")
fasttext_langs = []
fasttext_probs = []

for text in texts:
    if len(text) < 5:
        fasttext_langs.append('unknown')
        fasttext_probs.append(0.0)
    else:
        predictions = ft_model.predict(text, k=1)
        lang = predictions[0][0].replace('__label__', '')
        prob = float(predictions[1][0])
        fasttext_langs.append(lang)
        fasttext_probs.append(round(prob, 4))

df['lang_fasttext'] = fasttext_langs
df['lang_prob'] = fasttext_probs

# Also run langdetect validation on non-en or low-confidence samples to ensure zero false positives
def validate_with_langdetect(row):
    text = (str(row.get('review_title', '')) + ' ' + str(row.get('review_text', ''))).strip()
    ft_lang = row['lang_fasttext']
    ft_prob = row['lang_prob']
    
    # High confidence fasttext English -> accept
    if ft_lang == 'en' and ft_prob >= 0.75:
        return 'en', ft_prob
    
    # If fasttext says non-English or low confidence, double-check with langdetect
    if len(text) >= 10:
        try:
            ld_res = detect_langs(text)
            top = ld_res[0]
            if top.lang == 'en' and top.prob >= 0.75:
                return 'en', round(top.prob, 4)
            else:
                return top.lang, round(top.prob, 4)
        except Exception:
            pass
    return ft_lang, ft_prob

print("\nCross-validating non-English / low-confidence samples with langdetect...")

# Identify suspicious or non-English rows to validate with langdetect
mask_check = (df['lang_fasttext'] != 'en') | (df['lang_prob'] < 0.75)
print(f"Total non-English / low-confidence candidates to validate: {mask_check.sum()}")

final_langs = df['lang_fasttext'].tolist()
final_probs = df['lang_prob'].tolist()

sub_indices = df[mask_check].index.tolist()
for idx in sub_indices:
    row_title = str(df.at[idx, 'review_title'] or '')
    row_text = str(df.at[idx, 'review_text'] or '')
    text = (row_title + ' ' + row_text).strip()[:500]
    if len(text) >= 10:
        try:
            ld_res = detect_langs(text)
            top = ld_res[0]
            final_langs[idx] = top.lang
            final_probs[idx] = round(top.prob, 4)
        except Exception:
            pass

df['lang_final'] = final_langs
df['lang_prob_final'] = final_probs

# Strictly set is_english: lang_final == 'en' AND prob >= 0.70
df['is_english_new'] = ((df['lang_final'] == 'en') & (df['lang_prob_final'] >= 0.70)).astype(int)

print("\n=======================================================")
print("Language Identification Audit Results:")
print("=======================================================")
print("Final Language Breakdown (Top 15):")
print(df['lang_final'].value_counts().head(15).to_string())

old_en_count = (df['is_english'] == 1).sum()
new_en_count = (df['is_english_new'] == 1).sum()

print(f"\nPrevious English Count: {old_en_count} ({old_en_count/len(df)*100:.2f}%)")
print(f"New Strict English Count: {new_en_count} ({new_en_count/len(df)*100:.2f}%)")
print(f"Purged Non-English Reviews from English set: {old_en_count - new_en_count}")

false_en = df[(df['is_english'] == 1) & (df['is_english_new'] == 0)]
print(f"\nCaught False-Positive English Reviews: {len(false_en)}")

if len(false_en) > 0:
    print("\nSample Purged Non-English Reviews:")
    print(false_en[['review_title', 'review_text', 'lang_final', 'lang_prob_final', 'sentiment_polarity', 'rating']].head(10).to_string())

# Apply changes to dataset
df['language'] = df['lang_final']
df['is_english'] = df['is_english_new']

# Drop intermediate temporary columns
df.drop(columns=['lang_fasttext', 'lang_prob', 'lang_final', 'lang_prob_final', 'is_english_new'], inplace=True, errors='ignore')

# Re-compute VADER sentiment scores
print("\nRe-calculating VADER sentiment scores...")
sentiments = df['review_text'].fillna('').apply(lambda x: sia.polarity_scores(str(x)) if str(x) else {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0})
df['sentiment_polarity'] = [s['compound'] for s in sentiments]
df['sentiment_pos'] = [s['pos'] for s in sentiments]
df['sentiment_neg'] = [s['neg'] for s in sentiments]

# Save datasets
master_out = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
non_eng_out = 'data/cleaned_datasets/non_english_reviews.csv'

df.to_csv(master_out, index=False, encoding='utf-8-sig')
df[df['is_english'] == 0].to_csv(non_eng_out, index=False, encoding='utf-8-sig')

print(f"\nSaved updated Master Dataset ({len(df)} rows) -> {master_out}")
print(f"Saved Non-English Reviews ({(df['is_english']==0).sum()} rows) -> {non_eng_out}")
