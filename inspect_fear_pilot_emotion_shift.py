import pandas as pd
import re
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
df = pd.read_csv(master_path)
df = df[df['is_english'] == 1].copy()

fear_words = {'fear', 'nervous', 'scared', 'afraid', 'anxious', 'terrified', 'frightened'}

records = []
for idx, row in df.iterrows():
    rating = row['rating']
    if rating != 5:
        continue
    text = str(row['review_title']) + " . " + str(row['review_text'])
    text_lower = text.lower()
    
    found_words = [w for w in fear_words if re.search(r'\b' + w + r'\b', text_lower)]
    if not found_words:
        continue
        
    has_pilot = row['pilot_mention'] == 1 or bool(re.search(r'\b(pilot|captain|guide|bruce|carla|ken|mike|dave|mark)\b', text_lower))
    
    # Extract sentences containing fear words
    sentences = re.split(r'[.!?\n]+', text)
    fear_sents = []
    pilot_sents = []
    for s in sentences:
        s_strip = s.strip()
        if any(re.search(r'\b' + w + r'\b', s_strip.lower()) for w in fear_words):
            fear_sents.append(s_strip)
        if re.search(r'\b(pilot|captain|guide|bruce|carla|ken|mike|dave|mark)\b', s_strip.lower()):
            pilot_sents.append(s_strip)
            
    records.append({
        'tour_name': row['tour_name'],
        'rating': rating,
        'fear_words': ", ".join(found_words),
        'has_pilot': 1 if has_pilot else 0,
        'fear_sentence': " | ".join(fear_sents[:2]),
        'pilot_sentence': " | ".join(pilot_sents[:2]),
        'full_text': text[:300] + '...'
    })

results_df = pd.DataFrame(records)
print(f"Total 5-Star Reviews with Fear/Nervous Words: {len(results_df)}")
print(f"Percentage mentioning Pilot/Captain: {(results_df['has_pilot'].mean()*100):.2f}%")

# Save detailed inspection CSV
out_csv = 'data/derived_outputs/fear_pilot_emotion_shift_cases.csv'
results_df.to_csv(out_csv, index=False, encoding='utf-8-sig')
print(f"Saved detailed emotion shift cases to {out_csv}")

print("\n--- SAMPLE 10 REAL EMOTION SHIFT SENTENCES ---")
for idx, r in results_df.head(10).iterrows():
    print(f"\n[Case {idx+1}] Words: {r['fear_words']} | Pilot Mentioned: {r['has_pilot']}")
    print(f"   Fear Context : {r['fear_sentence']}")
    print(f"   Pilot Context: {r['pilot_sentence']}")
