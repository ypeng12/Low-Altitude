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

# 2. Verification of Incongruence Table (High Rating 4+5 Star Reviews N=21,714)
high_df = df[df['rating'] >= 4].copy()
total_high = len(high_df)

vader_neg_comp = (high_df['sentiment_polarity'] < 0).sum()
vader_neg_prop_gt0 = (high_df['sentiment_neg'] > 0).sum()
vader_neg_prop_gte05 = (high_df['sentiment_neg'] >= 0.05).sum()

# Compute NRC scores if present or load from dataset / NRCLex
nrc_neg_cols = [c for c in high_df.columns if 'nrc_negative' in c]
if nrc_neg_cols:
    high_df['nrc_neg_score'] = high_df[nrc_neg_cols[0]]
else:
    print("Calculating NRC negative scores on the fly for audit...")
    from nrclex import NRCLex
    nrc_obj = NRCLex()
    nrc_negs = []
    for txt in high_df['review_text']:
        if not isinstance(txt, str) or not txt.strip():
            nrc_negs.append(0.0)
            continue
        words = re.findall(r'\b\w+\b', txt.lower())
        w_cnt = len(words) if len(words) > 0 else 1
        nrc_obj.load_token_list(words)
        nrc_negs.append(nrc_obj.raw_emotion_scores.get('negative', 0) / w_cnt)
    high_df['nrc_neg_score'] = nrc_negs

nrc_neg_gt0 = (high_df['nrc_neg_score'] > 0).sum()
nrc_neg_gte02 = (high_df['nrc_neg_score'] >= 0.02).sum()
both_neg = ((high_df['nrc_neg_score'] > 0) & (high_df['sentiment_neg'] > 0)).sum()

print("\n=======================================================")
print("2. VADER & NRC Negative Component Audit (High Rating 4+5 Star Reviews)")
print("=======================================================")
print(f"Total High Rating Reviews (Rating >= 4): N={total_high}")
print(f"  - VADER Compound < 0: {vader_neg_comp} ({vader_neg_comp/total_high*100:.2f}%)")
print(f"  - VADER Neg Prop > 0: {vader_neg_prop_gt0} ({vader_neg_prop_gt0/total_high*100:.2f}%)")
print(f"  - VADER Neg Prop >= 0.05: {vader_neg_prop_gte05} ({vader_neg_prop_gte05/total_high*100:.2f}%)")
print(f"  - NRC Negative > 0: {nrc_neg_gt0} ({nrc_neg_gt0/total_high*100:.2f}%)")
print(f"  - NRC Negative >= 0.02: {nrc_neg_gte02} ({nrc_neg_gte02/total_high*100:.2f}%)")
print(f"  - Both NRC & VADER Detect Negative: {both_neg} ({both_neg/total_high*100:.2f}%)")

# 3. Word-Level VADER Polarity vs. Mean Rating Correlation Audit
print("\n=======================================================")
print("3. Word-Level VADER Polarity vs. Mean Review Rating Correlation Audit")
print("=======================================================")
from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(min_df=20, stop_words='english', token_pattern=r'\b[a-zA-Z]{3,}\b')
X = cv.fit_transform(df['review_text'].fillna(''))
words = cv.get_feature_names_out()
ratings = df['rating'].values

# Compute mean rating per word using matrix multiplication
word_counts = np.array(X.sum(axis=0)).flatten()
word_rating_sums = np.array(X.T.dot(ratings)).flatten()
mean_ratings = word_rating_sums / word_counts

word_ratings = []
for w, m_rating, cnt in zip(words, mean_ratings, word_counts):
    v_score = sia.polarity_scores(w)['compound']
    word_ratings.append({'word': w, 'vader_compound': v_score, 'mean_rating': m_rating, 'freq': cnt})

word_df = pd.DataFrame(word_ratings)
corr_substantive = word_df['vader_compound'].corr(word_df['mean_rating'])
print(f"Substantive Words Evaluated (min_df=20): {len(word_df)}")
print(f"Substantive Word-Level VADER vs Mean Rating Pearson r: {corr_substantive:.4f}")

# CATE Curated Word Correlation
cate_csv = 'data/derived_outputs/cate_3sentiment_words_stats.csv'
corr_cate = 0.0
if os.path.exists(cate_csv):
    cate_df = pd.read_csv(cate_csv)
    if 'mean_polarity' in cate_df.columns and 'mean_rating' in cate_df.columns:
        corr_cate = cate_df['mean_polarity'].corr(cate_df['mean_rating'])
        print(f"CATE 107 Domain Adjectives Mean Polarity vs Mean Rating Pearson r: {corr_cate:.4f}")

# 4. ABSA & Discourse Dynamics Verification
print("\n=======================================================")
print("4. ABSA & Discourse Dynamics Verification")
print("=======================================================")
pilot_pos_cnt = (df['pilot_pos'] == 1).sum() if 'pilot_pos' in df.columns else 0
pilot_neg_cnt = (df['pilot_neg'] == 1).sum() if 'pilot_neg' in df.columns else 0
weather_pos_cnt = (df['weather_pos'] == 1).sum() if 'weather_pos' in df.columns else 0
weather_neg_cnt = (df['weather_neg'] == 1).sum() if 'weather_neg' in df.columns else 0
safety_assure_cnt = (df['safety_assurance'] == 1).sum() if 'safety_assurance' in df.columns else 0
fear_anx_cnt = (df['fear_anxiety'] == 1).sum() if 'fear_anxiety' in df.columns else 0
fear_trans_cnt = (df['fear_trans'] == 1).sum() if 'fear_trans' in df.columns else 0
post_but_cnt = (df['has_adversative_conjunction'] == 1).sum() if 'has_adversative_conjunction' in df.columns else 0

print(f"  - Pilot Positive Polarity: {pilot_pos_cnt} ({pilot_pos_cnt/total_n*100:.2f}%) | Negative: {pilot_neg_cnt} ({pilot_neg_cnt/total_n*100:.2f}%)")
print(f"  - Weather Positive Polarity: {weather_pos_cnt} ({weather_pos_cnt/total_n*100:.2f}%) | Negative: {weather_neg_cnt} ({weather_neg_cnt/total_n*100:.2f}%)")
print(f"  - Safety Assurance: {safety_assure_cnt} ({safety_assure_cnt/total_n*100:.2f}%) | Fear/Anxiety: {fear_anx_cnt} ({fear_anx_cnt/total_n*100:.2f}%) | Fear Transformation: {fear_trans_cnt} ({fear_trans_cnt/total_n*100:.2f}%)")
print(f"  - Reviews with Adversative Conjunction ('but'): {post_but_cnt} ({post_but_cnt/total_n*100:.2f}%)")

# 5. Verification of 2,161 Sub-Cohort High-Rating Local-Negative Phenomena Ratios
print("\n=======================================================")
print("5. Verification of Sub-Cohort (N=2,161: English, Rating>=4, NegProp>=0.05)")
print("=======================================================")
sub_cohort = en_df[(en_df['rating'] >= 4) & (en_df['sentiment_neg'] >= 0.05)].copy()
n_sub = len(sub_cohort)
print(f"Sub-Cohort Total Rows: N = {n_sub}")

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

print(f"  1. Contrast/Concession Markers (but/however...): {c_contrast} ({c_contrast/n_sub*100:.1f}%)")
print(f"  2. Weather/Uncontrollable Factor Mention: {c_weather} ({c_weather/n_sub*100:.1f}%)")
print(f"  3. Price/Value Concession Mention: {c_price} ({c_price/n_sub*100:.1f}%)")
print(f"  4. Fear/Physiological Arousal Mention: {c_fear} ({c_fear/n_sub*100:.1f}%)")
print(f"  5. Service Recovery/Reassurance Mention: {c_recovery} ({c_recovery/n_sub*100:.1f}%)")
print(f"  6. Direct Staff Negative Expression: {c_staff_neg} ({c_staff_neg/n_sub*100:.1f}%)")

# Save complete audit verification table
audit_df = pd.DataFrame([
    {"definition": "Total Master Reviews", "count": total_n, "percentage": 100.0},
    {"definition": "5-Star Reviews", "count": s5_cnt, "percentage": round(s5_cnt/total_n*100, 2)},
    {"definition": "4+5 Star Reviews", "count": s45_cnt, "percentage": round(s45_cnt/total_n*100, 2)},
    {"definition": "VADER 整篇 compound 小于 0", "count": vader_neg_comp, "percentage": round(vader_neg_comp/total_high*100, 2)},
    {"definition": "VADER negative proportion 大于 0", "count": vader_neg_prop_gt0, "percentage": round(vader_neg_prop_gt0/total_high*100, 2)},
    {"definition": "VADER negative proportion 至少 0.05", "count": vader_neg_prop_gte05, "percentage": round(vader_neg_prop_gte05/total_high*100, 2)},
    {"definition": "NRC negative 大于 0", "count": nrc_neg_gt0, "percentage": round(nrc_neg_gt0/total_high*100, 2)},
    {"definition": "NRC negative 至少 0.02", "count": nrc_neg_gte02, "percentage": round(nrc_neg_gte02/total_high*100, 2)},
    {"definition": "NRC 与 VADER 都检测到某种负面成分", "count": both_neg, "percentage": round(both_neg/total_high*100, 2)},
    {"definition": "CATE Domain Adjectives Mean Polarity vs Mean Rating r", "count": len(cate_df) if os.path.exists(cate_csv) else 0, "percentage": round(corr_cate, 4)},
    {"definition": "Substantive Word VADER vs Mean Rating r", "count": len(word_df), "percentage": round(corr_substantive, 4)},
    {"definition": "ABSA Pilot Positive Polarity", "count": pilot_pos_cnt, "percentage": round(pilot_pos_cnt/total_n*100, 2)},
    {"definition": "ABSA Pilot Negative Polarity", "count": pilot_neg_cnt, "percentage": round(pilot_neg_cnt/total_n*100, 2)},
    {"definition": "ABSA Weather Negative Polarity", "count": weather_neg_cnt, "percentage": round(weather_neg_cnt/total_n*100, 2)},
    {"definition": "Safety Assurance (Positive)", "count": safety_assure_cnt, "percentage": round(safety_assure_cnt/total_n*100, 2)},
    {"definition": "Fear/Anxiety (Negative)", "count": fear_anx_cnt, "percentage": round(fear_anx_cnt/total_n*100, 2)},
    {"definition": "Fear-to-Safety Transformation Index", "count": fear_trans_cnt, "percentage": round(fear_trans_cnt/total_n*100, 2)},
    {"definition": "Adversative Conjunction ('but' clause)", "count": post_but_cnt, "percentage": round(post_but_cnt/total_n*100, 2)}
])

out_table_path = 'data/derived_outputs/deep_research_audit_verification.csv'
audit_df.to_csv(out_table_path, index=False, encoding='utf-8-sig')
print(f"\nSaved Deep Research Audit Verification Table -> {out_table_path}")
