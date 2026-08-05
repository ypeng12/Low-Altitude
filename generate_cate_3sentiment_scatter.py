import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import sys
from nltk.corpus import stopwords
from adjustText import adjust_text

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# 1. Load Master Dataset and User's Exact Manually Curated CATE Words (N=107)
master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
cate_path = 'data/derived_outputs/cate_words_full_224.csv'

print(f"Loading master dataset from {master_path}...")
df = pd.read_csv(master_path)
df_eng = df[df['is_english'] == 1].copy()

cate_df = pd.read_csv(cate_path)
cate_words_dict = {}

for idx, row in cate_df.iterrows():
    w_raw = str(row['CATE 词汇']).strip()
    w_match = re.match(r'^([a-zA-Z\-]+)', w_raw)
    if w_match:
        w_lower = w_match.group(1).lower()
        cate_words_dict[w_lower] = {
            'raw': w_raw,
            'original_cate': str(row['语义类别']).strip()
        }

print(f"Strictly loaded {len(cate_words_dict)} user-curated CATE words from {cate_path}.")

# Calculate word-level statistics from master reviews
stop_words = set(stopwords.words('english'))
word_stats = {w: {'ratings': [], 'polarities': [], 'count': 0} for w in cate_words_dict}

for idx, row in df.iterrows():
    rating = row['rating']
    polarity = row['sentiment_polarity']
    text = str(row['review_title']) + " " + str(row['review_text'])
    tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
    
    for token in tokens:
        if token in word_stats:
            word_stats[token]['ratings'].append(rating)
            word_stats[token]['polarities'].append(polarity)
            word_stats[token]['count'] += 1

# Explicit 3 Sentiment Category Definitions based on word meaning & sentiment scores
neg_words = {'wrong', 'uncomfortable', 'lack', 'boring', 'suffer', 'chilly', 'delayed', 'bother', 'cramped', 'inclement', 'tired', 'skeptical'}
neutral_words = {
    'small', 'extra', 'cold', 'noise', 'standing', 'actual', 'inaccessible', 'culture', 
    'overcast', 'question', 'contact', 'accessible', 'spirit', 'balance', 'fair', 
    'flexibility', 'decent', 'extensive', 'impression', 'cute', 'chatty', 'silk', 
    'timely', 'carefully', 'communicative', 'comprehensive', 'diverse', 'inexpensive', 
    'courtesy', 'chilly', 'suitable', 'granted', 'leisurely', 'valuable', 'energetic', 
    'charm', 'comprehend', 'hooked', 'essential', 'balanced', 'effort', 'advantage', 
    'afford', 'agree', 'greater', 'kindness', 'superior', 'solid', 'educated', 'stellar'
}

records = []
for word, stats in word_stats.items():
    if stats['count'] == 0:
        continue
    w_lower = word.lower()
    mean_rat = np.mean(stats['ratings'])
    mean_pol = np.mean(stats['polarities'])
    
    if w_lower in neg_words or mean_rat < 4.6 or mean_pol < 0.80:
        cat3 = 'Negative Sentiment / Friction'
    elif w_lower in neutral_words or (0.80 <= mean_pol <= 0.90 and mean_rat <= 4.88 and w_lower not in ['worth', 'cool', 'ease', 'personable', 'unbelievable', 'calm', 'skilled']):
        cat3 = 'Neutral / Attribute & Operational'
    else:
        cat3 = 'Positive Sentiment / Delight'
        
    records.append({
        'word': word,
        'raw_label': cate_words_dict[word]['raw'],
        'count': stats['count'],
        'mean_rating': mean_rat,
        'mean_polarity': mean_pol,
        'sentiment_category': cat3
    })

cate_result_df = pd.DataFrame(records)
print(f"Generated stats for {len(cate_result_df)} user-curated CATE words into 3 Sentiment Categories:")
print(cate_result_df['sentiment_category'].value_counts())

# Save to CSV
cate_result_df.to_csv('data/derived_outputs/cate_3sentiment_words_stats.csv', index=False)

# -------------------------------------------------------------
# Generate Publication-Grade CATE 3-Sentiment Scatter Plot
# -------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(13.5, 8.8), dpi=300)

COLOR_MAP = {
    'Positive Sentiment / Delight': '#2CA02C',         # Green
    'Neutral / Attribute & Operational': '#E6A100',    # Amber / Warm Gold
    'Negative Sentiment / Friction': '#D62728'         # Red
}

cat_counts = cate_result_df['sentiment_category'].value_counts()
cats_order = ['Positive Sentiment / Delight', 'Neutral / Attribute & Operational', 'Negative Sentiment / Friction']

for cat in cats_order:
    sub = cate_result_df[cate_result_df['sentiment_category'] == cat]
    if len(sub) == 0:
        continue
    color = COLOR_MAP[cat]
    sizes = 45 + 38 * np.log10(sub['count'])
    
    ax.scatter(
        sub['mean_polarity'], sub['mean_rating'],
        c=color, s=sizes, label=f"{cat} (n={len(sub)})",
        alpha=0.85, edgecolors='black', linewidths=0.6, zorder=3
    )

dataset_mean_rating = df['rating'].mean()
ax.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.5, zorder=2, label=f'Dataset Mean Rating ({dataset_mean_rating:.2f})')
ax.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2, zorder=2)

# Select key representative words across all 3 categories to annotate
texts = []
annotate_words = [
    # Positive
    'worth', 'cool', 'ease', 'personable', 'unbelievable', 'calm', 'skilled', 'courteous', 
    'superb', 'strongly', 'polite', 'crystal', 'grandeur', 'extraordinary', 'hospitality', 
    'priceless', 'seasoned', 'adventurous', 'charming', 'fascinating', 'grateful',
    # Neutral
    'small', 'extra', 'organized', 'noise', 'cheap', 'flexibility', 'timely', 'diverse', 'cold', 'contact',
    'working', 'attention', 'question', 'overcast', 'accessible', 'inaccessible', 'spirit',
    # Negative
    'uncomfortable', 'lack', 'boring', 'wrong', 'delayed', 'cramped', 'bother', 'suffer', 'chilly', 'tired', 'skeptical'
]

for idx, row in cate_result_df.iterrows():
    w = row['word']
    if w in annotate_words:
        txt = ax.text(
            row['mean_polarity'], row['mean_rating'],
            w, fontsize=9.5, fontweight='bold', alpha=0.9, zorder=4
        )
        texts.append(txt)

adjust_text(
    texts,
    arrowprops=dict(arrowstyle='->', color='gray', lw=0.6, alpha=0.7),
    expand_text=(1.2, 1.3),
    expand_points=(1.2, 1.3),
    force_text=(0.5, 0.8),
    force_points=(0.5, 0.8)
)

ax.set_title('User-Curated CATE Keyword Sentiment Scatter Plot (N=107): 3 Sentiment Tiers', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Average VADER Sentiment Polarity (-1.0 to +1.0)', fontsize=12, labelpad=10)
ax.set_ylabel('Average Tourist Star Rating (1.0 to 5.0 Stars)', fontsize=12, labelpad=10)

ax.legend(title='CATE Sentiment Categories', fontsize=10.5, title_fontsize=11.5, loc='lower right', frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()
os.makedirs('figures', exist_ok=True)
out_fig = 'figures/cate_3sentiment_scatter.png'
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved user-curated 3-sentiment CATE scatter plot to {out_fig}")
