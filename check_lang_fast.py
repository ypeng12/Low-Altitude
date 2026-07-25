import pandas as pd
import re

df = pd.read_csv('tripadvisor_level1_cleaned.csv')
total = len(df)

# Common English words
english_stopwords = {'the', 'and', 'is', 'was', 'in', 'to', 'of', 'it', 'for', 'with', 'on', 'that', 'this', 'we', 'our', 'my', 'had', 'were'}

def detect_non_english(text):
    if not isinstance(text, str) or len(text.strip()) == 0:
        return 'Unknown'
    
    # 1. Non-latin script check (Chinese, Japanese, Korean, Cyrillic, Arabic)
    if re.search(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\u0400-\u04ff\u0600-\u06ff]', text):
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'Chinese'
        elif re.search(r'[\u3040-\u30ff]', text):
            return 'Japanese'
        elif re.search(r'[\uac00-\ud7af]', text):
            return 'Korean'
        elif re.search(r'[\u0400-\u04ff]', text):
            return 'Russian'
        else:
            return 'Other Non-Latin'
            
    # 2. Latin-based non-English check (French, German, Spanish, Portuguese, Italian)
    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    if len(words) >= 5:
        # Count overlap with core English words
        overlap = words.intersection(english_stopwords)
        if len(overlap) == 0:
            # Check specific language markers
            if any(w in words for w in ['le', 'la', 'les', 'du', 'et', 'est', 'très', 'magnifique', 'pour', 'une', 'des']):
                return 'French'
            elif any(w in words for w in ['der', 'die', 'das', 'und', 'ist', 'mit', 'sehr', 'schön', 'war', 'ein', 'eine']):
                return 'German'
            elif any(w in words for w in ['el', 'la', 'los', 'las', 'que', 'muy', 'excelente', 'con', 'para', 'por']):
                return 'Spanish'
            elif any(w in words for w in ['il', 'che', 'molto', 'bello', 'per', 'con', 'vista', 'della']):
                return 'Italian'
            else:
                return 'Other Latin Non-English'
    
    return 'English'

df['lang_cat'] = (df['review_title'].fillna('') + ' ' + df['review_text'].fillna('')).apply(detect_non_english)

print("\n--- FAST LANGUAGE DETECTOR RESULTS ---")
print(df['lang_cat'].value_counts())

non_en = df[df['lang_cat'] != 'English']
print(f"\nTotal Non-English Reviews: {len(non_en)} out of {total} ({len(non_en)/total*100:.2f}%)")
print(f"Total English Reviews: {total - len(non_en)} ({((total - len(non_en))/total*100):.2f}%)")
