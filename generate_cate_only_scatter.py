import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import sys
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from adjustText import adjust_text

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure NLTK resources
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

sia = SentimentIntensityAnalyzer()
vader_lexicon = sia.lexicon

# 1. Load Master Dataset & 107 Curated CATE Words
master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
cate_path = 'data/derived_outputs/cate_words_curated_107.csv'

print(f"Loading master dataset from {master_path}...")
df_raw = pd.read_csv(master_path)
df = df_raw[df_raw['is_english'] == 1].copy()
print(f"Total Master Reviews: {len(df_raw)} | Filtered Pure English Reviews: {len(df)}")

# Load 107 CATE words
cate_df = pd.read_csv(cate_path)
cate_words_dict = {}
for idx, row in cate_df.iterrows():
    w_raw = str(row['CATE 词汇']).strip()
    w_match = re.match(r'^([a-zA-Z\-]+)', w_raw)
    if w_match:
        w_lower = w_match.group(1).lower()
        cate_words_dict[w_lower] = w_raw

print(f"Loaded {len(cate_words_dict)} CATE adjectives.")

# 2. Calculate word-level statistics for CATE 107 words
word_stats = {w: {'ratings': [], 'count': 0} for w in cate_words_dict}

for idx, row in df.iterrows():
    rating = row['rating']
    text = str(row['review_title']) + " " + str(row['review_text'])
    tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
    
    for token in tokens:
        if token in word_stats:
            word_stats[token]['ratings'].append(rating)
            word_stats[token]['count'] += 1

records = []
for word, stats in word_stats.items():
    if stats['count'] > 0:
        mean_rating = np.mean(stats['ratings'])
        raw_vader = vader_lexicon.get(word, 0.0)
        records.append({
            'word': word,
            'raw_label': cate_words_dict[word],
            'count': stats['count'],
            'mean_rating': mean_rating,
            'raw_vader_score': raw_vader
        })

cate_only_df = pd.DataFrame(records)
dataset_mean_rating = df['rating'].mean()

# Save stats CSV
out_csv = 'data/derived_outputs/cate_only_107_vader_stats.csv'
cate_only_df.to_csv(out_csv, index=False, encoding='utf-8-sig')
print(f"Saved CATE Only stats to {out_csv}")

# 3. Plot CATE Only Scatter Plot
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(15.0, 10.0), dpi=300)

sizes = 45 + 36 * np.log10(cate_only_df['count'])

ax.scatter(
    cate_only_df['raw_vader_score'], cate_only_df['mean_rating'],
    c='#FFE500', s=sizes, alpha=0.92, edgecolors='black', linewidths=0.8, zorder=3, label='CATE Domain Attributes (n=107)'
)

ax.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.5, zorder=2, label=f'Dataset Mean Rating ({dataset_mean_rating:.2f})')
ax.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2, zorder=2)

# Annotate CATE words
texts = []
curated_cate_labels = {
    'worth', 'small', 'interesting', 'cool', 'extra', 'ease', 'personable', 'unbelievable', 'calm',
    'skilled', 'choice', 'courteous', 'organized', 'cheap', 'overcast', 'accessible', 'inaccessible',
    'priceless', 'epic', 'grandeur', 'convenient', 'hospitality', 'uncomfortable', 'lack', 'careful',
    'delayed', 'wrong', 'strongly', 'balance', 'crystal', 'fair'
}

for idx, row in cate_only_df.iterrows():
    w = row['word']
    x = row['raw_vader_score']
    y = row['mean_rating']
    
    if w in curated_cate_labels or x < -0.5 or y < 4.6:
        txt = ax.text(x, y, w, fontsize=8.5, fontweight='normal', color='#1E293B', alpha=0.95, zorder=5)
        texts.append(txt)

adjust_text(
    texts,
    arrowprops=dict(arrowstyle='->', color='#64748B', lw=0.6, alpha=0.75),
    expand_text=(1.25, 1.35),
    expand_points=(1.25, 1.35),
    force_text=(0.6, 0.9),
    force_points=(0.6, 0.9)
)

ax.set_title('CATE 107 Domain Attributes Only Scatter Plot: Raw VADER Score (-4.0 to +4.0) vs Tourist Rating (1.0 to 5.0)\n[Gold Highlighting, Unified Dark Text Labels]', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Raw Inherent VADER Word Polarity Score (-4.0 to +4.0 Scale)', fontsize=12, labelpad=10)
ax.set_ylabel('Average Tourist Star Rating (1.0 to 5.0 Stars)', fontsize=12, labelpad=10)
ax.set_xlim(-4.0, +4.0)

ax.legend(fontsize=10, loc='lower left', frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()
out_dir = 'figures/cate_sentiment_plots'
os.makedirs(out_dir, exist_ok=True)
out_fig = os.path.join(out_dir, 'cate_107_only_scatter.png')
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()

print(f"Saved CATE Only scatter plot to {out_fig}")
