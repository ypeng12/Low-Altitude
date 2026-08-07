import pandas as pd
import numpy as np
import re
import os
import sys
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sys.stdout.reconfigure(encoding='utf-8')

sia = SentimentIntensityAnalyzer()

master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
print(f"Loading master dataset from {master_path}...")
df = pd.read_csv(master_path)
print(f"Total Master Rows: {len(df)}")

# Aspect Category Regex Patterns
ASPECT_PATTERNS = {
    'Scenery': r'\b(view|views|scenery|landscape|canyon|glacier|mountain|mountains|waterfall|coast|scenic|grandeur|cliff|sea|ocean|island|wildlife)\b',
    'Pilot': r'\b(pilot|pilots|captain|bruce|toby|mark|david|john|michael|alex|aviator)\b',
    'GroundStaff': r'\b(staff|desk|check-in|counter|reception|office|ground|boarding|driver|shuttle|agent|team)\b',
    'CabinComfort': r'\b(seat|seats|seating|cramped|small|tight|noise|noisy|headset|headphones|cold|wind|window|legroom|comfort|uncomfortable)\b',
    'Safety': r'\b(safe|safety|scared|nervous|afraid|fear|terrified|anxious|worry|worried|comforting|reassured|calm|secure)\b',
    'Weather': r'\b(weather|cloud|clouds|cloudy|wind|winds|windy|rain|fog|foggy|snow|visibility|overcast)\b',
    'PriceValue': r'\b(price|prices|expensive|cost|costs|costly|worth|money|value|dollar|dollars|cash|cheap|affordable)\b',
    'ServiceRecovery': r'\b(refund|refunded|reschedule|rescheduled|alternative|delay|delayed|cancel|cancelled|cancellation|accommodated|fix|fixed)\b',
    'Companion': r'\b(husband|wife|family|kids|children|son|daughter|mom|dad|friend|friends|couple|honeymoon|anniversary)\b',
    'LifetimeExperience': r'\b(bucket list|once in a lifetime|unforgettable|dream|experience of a lifetime|must do|highlight)\b'
}

def extract_aspects(text):
    if not isinstance(text, str):
        return []
    found = []
    text_lower = text.lower()
    for aspect, pattern in ASPECT_PATTERNS.items():
        if re.search(pattern, text_lower):
            found.append(aspect)
    return found

print("\nExtracting Aspect Mentions across 10 Target Domains...")
df['aspects_found'] = df['review_text'].apply(extract_aspects)
df['aspect_count'] = df['aspects_found'].apply(len)

for aspect in ASPECT_PATTERNS.keys():
    df[f'aspect_{aspect}'] = df['aspects_found'].apply(lambda x: 1 if aspect in x else 0)

print("Aspect Prevalence Summary:")
for aspect in ASPECT_PATTERNS.keys():
    cnt = df[f'aspect_{aspect}'].sum()
    pct = cnt / len(df) * 100
    print(f"  - {aspect}: {cnt} ({pct:.2f}%)")

# Incongruence Taxonomy Categorization
def categorize_incongruence(row):
    text = str(row.get('review_text', '')).lower()
    rating = row.get('rating', 5)
    v_comp = row.get('sentiment_polarity', 0.0)
    v_neg = row.get('sentiment_neg', 0.0)
    is_eng = row.get('is_english', 1)
    
    # Non-incongruent pure positive 5-star
    if rating >= 4 and v_comp >= 0.5 and v_neg < 0.02:
        return 'Pure Positive Baseline'
    
    # Low rating 1-3 star
    if rating <= 3:
        return 'Low Rating Failure'

    # Multilingual artifact
    if is_eng == 0 or row.get('language', 'en') != 'en':
        return 'Type 9: Multilingual Lexicon Artifact'
    
    # Negation pseudo-negative
    if re.search(r'\b(never felt unsafe|no problem|no problems|no delay|no delays|not dangerous|don\'t miss|cannot recommend enough)\b', text):
        return 'Type 8: Negation Pseudo-Negative'
        
    # Fear transformation
    if re.search(r'\b(scared|terrified|nervous|afraid|anxious|fear)\b', text) and re.search(r'\b(safe|reassured|calm|made us feel|great pilot|smooth)\b', text):
        return 'Type 3: Fear Transformation / Arousal'

    # Price concession
    if re.search(r'\b(expensive|costly|pricey|a bit steep|cost a lot)\b', text) and re.search(r'\b(worth|worth it|every penny|priceless|no regrets)\b', text):
        return 'Type 5: Price Concession'

    # Service recovery
    if re.search(r'\b(cancel|cancelled|cancellation|delay|delayed|weather change)\b', text) and re.search(r'\b(refund|refunded|rescheduled|accommodated|handled well|great service)\b', text):
        return 'Type 4: Service Recovery'

    # Uncontrollable natural factor
    if re.search(r'\b(cloud|clouds|cloudy|wind|fog|rain|weather)\b', text) and re.search(r'\b(pilot did best|still amazing|great view|understandable)\b', text):
        return 'Type 2: Uncontrollable Natural Factor'

    # Local friction overall positive
    if v_neg >= 0.05 or re.search(r'\b(cramped|tight|small|noise|noisy|bumpy|cold|waiting|long wait)\b', text):
        return 'Type 1: Local Friction - Overall Positive'

    # True star-text conflict
    if rating >= 4 and v_comp < 0:
        return 'Type 10: True Star-Text Conflict'

    return 'Minor Local Noise'

print("\nCategorizing Rating-Text Incongruence Taxonomy (10 Mechanisms)...")
df['incongruence_type'] = df.apply(categorize_incongruence, axis=1)

print("\nIncongruence Taxonomy Distribution (All Reviews):")
print(df['incongruence_type'].value_counts().to_string())

# Save Quintuple Extraction Dataset
out_dataset = 'data/derived_outputs/deep_research_quintuple_extracted.csv'
df.to_csv(out_dataset, index=False, encoding='utf-8-sig')
print(f"\nSaved Quintuple Extracted Dataset ({len(df)} rows) -> {out_dataset}")

# Save Incongruence Taxonomy Table
inc_summary = df['incongruence_type'].value_counts().reset_index()
inc_summary.columns = ['Incongruence_Mechanism', 'Review_Count']
inc_summary['Percentage'] = (inc_summary['Review_Count'] / len(df) * 100).round(2)
inc_summary_out = 'data/derived_outputs/incongruence_taxonomy_summary.csv'
inc_summary.to_csv(inc_summary_out, index=False, encoding='utf-8-sig')
print(f"Saved Incongruence Taxonomy Table -> {inc_summary_out}")
