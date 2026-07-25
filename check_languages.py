import pandas as pd
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 42

df = pd.read_csv('tripadvisor_level1_cleaned.csv')
print(f"Loaded total reviews: {len(df)}")

def get_lang(text):
    if not isinstance(text, str) or len(text.strip()) < 10:
        return 'unknown'
    try:
        return detect(text)
    except:
        return 'unknown'

df['language'] = df['review_text'].apply(get_lang)
vc = df['language'].value_counts()
print("\n--- LANGUAGE DISTRIBUTION SUMMARY ---")
print(vc)

non_en_count = (df['language'] != 'en').sum()
non_en_pct = (non_en_count / len(df)) * 100
print(f"\nEnglish Reviews: {(df['language'] == 'en').sum()} ({((df['language'] == 'en').sum()/len(df)*100):.2f}%)")
print(f"Non-English Reviews: {non_en_count} ({non_en_pct:.2f}%)")

df_non_en = df[df['language'] != 'en'][['tour_name', 'user_name', 'language', 'review_title', 'review_text']]
df_non_en.to_csv("non_english_reviews.csv", index=False)
print("Saved non-English reviews to non_english_reviews.csv")
