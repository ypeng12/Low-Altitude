import pandas as pd
import numpy as np
import re
import os
import sys
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nrclex import NRCLex

sys.stdout.reconfigure(encoding='utf-8')

master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
print(f"Loading master dataset from {master_path}...")
df = pd.read_csv(master_path)
print(f"Total Rows: {len(df)}")

sia = SentimentIntensityAnalyzer()

# Filter pure English reviews (is_english == 1) or analyze total
en_df = df[df['is_english'] == 1].copy()
print(f"Pure English Rows (is_english == 1): {len(en_df)}")

# 1. Verification of Rating Ceiling Distribution
total_n = len(df)
s5_cnt = (df['rating'] == 5).sum()
s45_cnt = (df['rating'] >= 4).sum()
avg_rating = df['rating'].mean()

print("\n=======================================================")
print("1. Rating Ceiling Distribution (Audit Verification)")
print("=======================================================")
print(f"Total Reviews: {total_n}")
print(f"5-Star Count: {s5_cnt} ({s5_cnt/total_n*100:.2f}%)")
print(f"4+5 Star Count: {s45_cnt} ({s45_cnt/total_n*100:.2f}%)")
print(f"Average Star Rating: {avg_rating:.3f}")

# 2. Verification of Incongruence Table (High Rating 4+5 Star Reviews)
high_df = df[df['rating'] >= 4].copy()
total_high = len(high_df)

high_en_df = en_df[en_df['rating'] >= 4].copy()
total_en_high = len(high_en_df)

vader_neg_comp = (high_df['sentiment_polarity'] < 0).sum()
vader_neg_prop_gt0 = (high_df['sentiment_neg'] > 0).sum()
vader_neg_prop_gte05 = (high_df['sentiment_neg'] >= 0.05).sum()

en_vader_neg_comp = (high_en_df['sentiment_polarity'] < 0).sum()
en_vader_neg_prop_gt0 = (high_en_df['sentiment_neg'] > 0).sum()
en_vader_neg_prop_gte05 = (high_en_df['sentiment_neg'] >= 0.05).sum()

print("\n=======================================================")
print("2. VADER & NRC Negative Component Audit (4+5 Star Reviews)")
print("=======================================================")
print(f"Raw High Rating Reviews (N={total_high}):")
print(f"  - VADER Compound < 0: {vader_neg_comp} ({vader_neg_comp/total_high*100:.2f}%)")
print(f"  - VADER Neg Prop > 0: {vader_neg_prop_gt0} ({vader_neg_prop_gt0/total_high*100:.2f}%)")
print(f"  - VADER Neg Prop >= 0.05: {vader_neg_prop_gte05} ({vader_neg_prop_gte05/total_high*100:.2f}%)")

print(f"\nStrict Pure English High Rating Reviews (N={total_en_high}):")
print(f"  - VADER Compound < 0: {en_vader_neg_comp} ({en_vader_neg_comp/total_en_high*100:.2f}%)")
print(f"  - VADER Neg Prop > 0: {en_vader_neg_prop_gt0} ({en_vader_neg_prop_gt0/total_en_high*100:.2f}%)")
print(f"  - VADER Neg Prop >= 0.05: {en_vader_neg_prop_gte05} ({en_vader_neg_prop_gte05/total_en_high*100:.2f}%)")

# 3. Verification of Discourse & Attribution Mechanisms (Lines 110-120)
# Sub-cohort: English, Rating >= 4, VADER Neg Prop >= 0.05
sub_cohort = en_df[(en_df['rating'] >= 4) & (en_df['sentiment_neg'] >= 0.05)].copy()
n_sub = len(sub_cohort)

print("\n=======================================================")
print(f"3. Discourse & Attribution Mechanism Heuristics (Sub-cohort N={n_sub})")
print("=======================================================")

# Discourse contrast/concession markers
contrast_pat = r'\b(but|however|although|though|despite|even though|nonetheless|yet)\b'
weather_pat = r'\b(weather|cloud|clouds|cloudy|wind|winds|windy|rain|fog|foggy|snow|delay|delays|delayed|cancel|cancelled|cancellation|turbulence|bumpy)\b'
price_pat = r'\b(price|prices|expensive|cost|costs|costly|worth|money|value|dollar|dollars|cash)\b'
fear_physio_pat = r'\b(scared|terrified|nervous|anxious|afraid|fear|frightened|sick|nausea|nauseous|dizzy|dizziness|cold|cramped|small|tight|noise|noisy)\b'
recovery_pat = r'\b(refund|refunded|reschedule|rescheduled|alternative|route|accommodate|accommodated|handled|reassured|reassurance|fix|fixed|help|helped)\b'
staff_neg_pat = r'\b(rude|unprofessional|disappointed|disappointing|poor|horrible|terrible|awful|bad|unfriendly)\b'

c_contrast = sub_cohort['review_text'].str.contains(contrast_pat, case=False, regex=True).sum()
c_weather = sub_cohort['review_text'].str.contains(weather_pat, case=False, regex=True).sum()
c_price = sub_cohort['review_text'].str.contains(price_pat, case=False, regex=True).sum()
c_fear = sub_cohort['review_text'].str.contains(fear_physio_pat, case=False, regex=True).sum()
c_recovery = sub_cohort['review_text'].str.contains(recovery_pat, case=False, regex=True).sum()
c_staff_neg = sub_cohort['review_text'].str.contains(staff_neg_pat, case=False, regex=True).sum()

print(f"1. Contrast/Concession Markers (but/however/although...): {c_contrast} ({c_contrast/n_sub*100:.1f}%)")
print(f"2. Weather/Uncontrollable Event Mention: {c_weather} ({c_weather/n_sub*100:.1f}%)")
print(f"3. Price/Value Mention: {c_price} ({c_price/n_sub*100:.1f}%)")
print(f"4. Fear/Physiological Discomfort Mention: {c_fear} ({c_fear/n_sub*100:.1f}%)")
print(f"5. Service Recovery/Reassurance Mention: {c_recovery} ({c_recovery/n_sub*100:.1f}%)")
print(f"6. Staff/Service Negative Expression Mention: {c_staff_neg} ({c_staff_neg/n_sub*100:.1f}%)")

# 4. Scenery vs. People Attribution Verification (Lines 603-617)
print("\n=======================================================")
print("4. Scenery vs. People Attribution Verification (Lines 603-617)")
print("=======================================================")

scenery_pos_pat = r'\b(view|views|scenery|landscape|canyon|glacier|mountain|mountains|waterfall|coast|scenic|breathtaking|spectacular|gorgeous|stunning|beautiful|amazing)\b'
people_pos_pat = r'\b(pilot|guide|staff|crew|captain|bruce|toby|mark|david|john|michael|alex|skilled|professional|personable|friendly|great pilot|excellent pilot|awesome pilot|wonderful pilot)\b'

# Loose Review-level
scenery_pos_loose = sub_cohort['review_text'].str.contains(scenery_pos_pat, case=False, regex=True)
people_pos_loose = sub_cohort['review_text'].str.contains(people_pos_pat, case=False, regex=True)

c_scenery_loose = scenery_pos_loose.sum()
c_people_loose = people_pos_loose.sum()
c_both_loose = (scenery_pos_loose & people_pos_loose).sum()
c_scenery_only = (scenery_pos_loose & (~people_pos_loose)).sum()
c_people_only = ((~scenery_pos_loose) & people_pos_loose).sum()

print("A. Loose Review-Level Matching:")
print(f"  - Scenery Positive Mention: {c_scenery_loose} ({c_scenery_loose/n_sub*100:.1f}%)")
print(f"  - People Positive Mention: {c_people_loose} ({c_people_loose/n_sub*100:.1f}%)")
print(f"  - Both Scenery & People Positive: {c_both_loose} ({c_both_loose/n_sub*100:.1f}%)")
print(f"  - Scenery Only Positive: {c_scenery_only} ({c_scenery_only/n_sub*100:.1f}%)")
print(f"  - People Only Positive: {c_people_only} ({c_people_only/n_sub*100:.1f}%)")

# Save audit verification table
audit_df = pd.DataFrame([
    {"metric": "Total Reviews", "count": total_n, "percentage": 100.0},
    {"metric": "5-Star Reviews", "count": s5_cnt, "percentage": round(s5_cnt/total_n*100, 2)},
    {"metric": "4+5 Star Reviews", "count": s45_cnt, "percentage": round(s45_cnt/total_n*100, 2)},
    {"metric": "Sub-cohort (High Rating & VADER Neg Prop >= 0.05)", "count": n_sub, "percentage": round(n_sub/total_en_high*100, 2)},
    {"metric": "Sub-cohort Contrast/Concession Markers", "count": c_contrast, "percentage": round(c_contrast/n_sub*100, 1)},
    {"metric": "Sub-cohort Weather/Uncontrollable Conditions", "count": c_weather, "percentage": round(c_weather/n_sub*100, 1)},
    {"metric": "Sub-cohort Price/Value Mention", "count": c_price, "percentage": round(c_price/n_sub*100, 1)},
    {"metric": "Sub-cohort Fear/Physical Discomfort", "count": c_fear, "percentage": round(c_fear/n_sub*100, 1)},
    {"metric": "Sub-cohort Service Recovery/Reassurance", "count": c_recovery, "percentage": round(c_recovery/n_sub*100, 1)},
    {"metric": "Sub-cohort Loose Scenery Positive", "count": c_scenery_loose, "percentage": round(c_scenery_loose/n_sub*100, 1)},
    {"metric": "Sub-cohort Loose People Positive", "count": c_people_loose, "percentage": round(c_people_loose/n_sub*100, 1)},
    {"metric": "Sub-cohort Loose Both Scenery & People", "count": c_both_loose, "percentage": round(c_both_loose/n_sub*100, 1)},
])

out_table_path = 'data/derived_outputs/deep_research_audit_verification.csv'
audit_df.to_csv(out_table_path, index=False, encoding='utf-8-sig')
print(f"\nSaved Deep Research Audit Table -> {out_table_path}")
