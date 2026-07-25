import pandas as pd
import numpy as np
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/cleaned_datasets/tripadvisor_processed_master.csv')

print("=== 1. 全量数据 VADER 情感极性全貌 ===")
print(df[['sentiment_polarity', 'sentiment_pos', 'sentiment_neg']].describe())

print("\n=== 2. 高积极 (Compound >= 0.8) vs 消极 (Compound <= -0.05) 样本规模 ===")
pos_df = df[df['sentiment_polarity'] >= 0.8]
neg_df = df[df['sentiment_polarity'] <= -0.05]
neu_df = df[(df['sentiment_polarity'] > -0.05) & (df['sentiment_polarity'] < 0.05)]

print(f"强积极样本 (Polarity >= 0.8): {len(pos_df)} 条 ({len(pos_df)/len(df)*100:.2f}%)")
print(f"中性/弱积极样本 (0.05 <= Polarity < 0.8): {len(df[(df['sentiment_polarity']>=0.05)&(df['sentiment_polarity']<0.8)])} 条 ({len(df[(df['sentiment_polarity']>=0.05)&(df['sentiment_polarity']<0.8)])/len(df)*100:.2f}%)")
print(f"中性样本 (-0.05 < Polarity < 0.05): {len(neu_df)} 条 ({len(neu_df)/len(df)*100:.2f}%)")
print(f"消极样本 (Polarity <= -0.05): {len(neg_df)} 条 ({len(neg_df)/len(df)*100:.2f}%)")

print("\n=== 3. 低空观光 9 大特征在【英文积极 vs 英文消极评论】中的出现率对比 ===")
eng_pos = df[(df['is_english']==1) & (df['sentiment_polarity'] >= 0.8)]
eng_neg = df[(df['is_english']==1) & (df['sentiment_polarity'] <= -0.05)]

features = [
    'safety_mention', 'pilot_mention', 'staff_service_mention', 
    'price_value_mention', 'weather_mention', 'helicopter_comparison',
    'canyon_mention', 'coast_mention', 'waterfall_mention', 'special_occasion'
]
print(f"{'特征维度 (Feature)':25s} | {'英文强积极提及率':12s} | {'英文消极提及率':12s} | {'结构比差异':10s}")
print("-" * 75)
for f in features:
    pos_rate = eng_pos[f].mean() * 100
    neg_rate = eng_neg[f].mean() * 100
    diff = neg_rate - pos_rate
    print(f"{f:25s} | {pos_rate:10.2f}% | {neg_rate:10.2f}% | {diff:+9.2f}%")

print("\n=== 4. 英文消极评论的主要痛点 (Negative Review Focus) ===")
# Filter English negative reviews
eng_neg_all = df[(df['is_english']==1) & (df['sentiment_polarity'] <= -0.05)]
print("英文消极评论总数:", len(eng_neg_all))

print("\n--- 英文消极评论 (Rating 1-2) 典型文本切片 ---")
low_rating_eng_neg = df[(df['is_english']==1) & (df['rating'] <= 2)].sort_values('sentiment_polarity').head(5)
for idx, row in low_rating_eng_neg.iterrows():
    print(f"Rating: {row['rating']} | Tour: {row['tour_name']} | Polarity: {row['sentiment_polarity']:.4f}")
    print(f"Title: {row['review_title']}")
    print(f"Text Snippet: {str(row['review_text'])[:150]}...\n")
