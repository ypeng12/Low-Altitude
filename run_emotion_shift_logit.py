import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import re
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# 1. Load Master Dataset
master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
print(f"Loading master dataset from {master_path}...")
df = pd.read_csv(master_path)

# Filter to English reviews
df_eng = df[df['is_english'] == 1].copy()

# Define binary high satisfaction target (5 stars vs <= 4 stars)
df_eng['high_satisfaction'] = (df_eng['rating'] == 5).astype(int)

# Extract presence of Fear emotion words (fear, nervous, scared, afraid, anxious)
fear_pattern = r'\b(?:fear|fearful|nervous|scared|afraid|anxious|terrified|scary)\b'
df_eng['has_fear'] = df_eng['review_text'].str.contains(fear_pattern, case=False, na=False).astype(int)

# Extract presence of Pilot Competence CATE words (pilot, captain, skilled, courteous, calm, professional, safe)
pilot_pattern = r'\b(?:pilot|captain|skilled|courteous|calm|professional|safe|experienced)\b'
df_eng['has_pilot_competence'] = df_eng['review_text'].str.contains(pilot_pattern, case=False, na=False).astype(int)

# Extract presence of Scenery CATE words (spectacular, breathtaking, scenic, view, epic, grandeur)
scenery_pattern = r'\b(?:spectacular|breathtaking|scenic|view|epic|grandeur|views|unbelievable)\b'
df_eng['has_scenery'] = df_eng['review_text'].str.contains(scenery_pattern, case=False, na=False).astype(int)

# Length of review (control variable)
df_eng['word_count'] = df_eng['review_text'].astype(str).str.split().str.len()
df_eng['log_word_count'] = np.log1p(df_eng['word_count'])

print(f"Dataset Total Reviews: {len(df_eng)}")
print(f"High Satisfaction (5-Star) Ratio: {df_eng['high_satisfaction'].mean():.2%}")
print(f"Reviews containing Fear words: {df_eng['has_fear'].sum()} ({df_eng['has_fear'].mean():.2%})")
print(f"Reviews containing Pilot Competence: {df_eng['has_pilot_competence'].sum()} ({df_eng['has_pilot_competence'].mean():.2%})")

# Fit Logistic Regression with Interaction Term (Fear * Pilot Competence)
print("\n=== Fitting Multivariate Logistic Regression for Emotion Shift Paradox ===")
logit_model = smf.logit(
    "high_satisfaction ~ has_fear + has_pilot_competence + has_fear:has_pilot_competence + has_scenery + log_word_count", 
    data=df_eng
).fit()

print(logit_model.summary())

# Calculate Odds Ratios and 95% Confidence Intervals
params = logit_model.params
conf = logit_model.conf_int()
conf['Odds Ratio'] = params
conf.columns = ['5%', '95%', 'Odds Ratio']
odds_ratios = np.exp(conf[['Odds Ratio', '5%', '95%']])
odds_ratios['p-value'] = logit_model.pvalues

print("\n=== Calculated Odds Ratios (OR) & 95% Confidence Intervals ===")
print(odds_ratios.to_string())

# Save regression table to derived_outputs
out_dir = 'data/derived_outputs'
os.makedirs(out_dir, exist_ok=True)
out_csv = os.path.join(out_dir, 'paper_table_emotion_shift_logit.csv')
odds_ratios.to_csv(out_csv)
print(f"\nSaved Emotion Shift Odds Ratio table to {out_csv}")
