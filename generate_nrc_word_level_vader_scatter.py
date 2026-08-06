import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import sys
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nrclex import NRCLex
from nltk.corpus import stopwords
from adjustText import adjust_text

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure NLTK VADER Lexicon is loaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

sia = SentimentIntensityAnalyzer()
vader_lexicon = sia.lexicon  # Inherent word-level sentiment scores (-4.0 to +4.0)

# 1. Load Master Dataset & Filter STRICTLY to English Reviews
master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
cate_path = 'data/derived_outputs/cate_words_curated_107.csv'

print(f"Loading master dataset from {master_path}...")
df_raw = pd.read_csv(master_path)
df = df_raw[df_raw['is_english'] == 1].copy()
print(f"Total Master Reviews: {len(df_raw)} | Filtered Pure English Reviews: {len(df)}")

# Load 107 CATE words
cate_words_set = set()
if os.path.exists(cate_path):
    cate_df = pd.read_csv(cate_path)
    for w in cate_df['CATE 词汇']:
        word_match = re.match(r'^([a-zA-Z\-]+)', str(w).strip())
        if word_match:
            cate_words_set.add(word_match.group(1).lower())

nrc_lexicon = NRCLex().__lexicon__
stop_words = set(stopwords.words('english'))

# Distinct Plutchik Pairwise Colors (High contrast, publication ready)
PLUTCHIK_COLORS = {
    'JOY': '#16A34A',          # Emerald Green (Joy)
    'SADNESS': '#64748B',      # Slate Blue-Grey (Sadness)
    'TRUST': '#1D4ED8',        # Royal Blue (Trust)
    'DISGUST': '#92400E',      # Muddy Brown (Disgust)
    'ANTICIPATION': '#EA580C', # Sunset Orange (Anticipation)
    'SURPRISE': '#9333EA',     # Neon Purple (Surprise)
    'FEAR': '#DC2626',         # Crimson Red (Fear/Thrill)
    'ANGER': '#B91C1C',        # Dark Blood Red (Anger)
    'CATE': '#FFE500'          # Brightest Electric Gold (Domain Priority)
}

def map_word_to_nrc_or_cate(word):
    w_lower = word.lower()
    if w_lower in cate_words_set:
        return 'CATE'
    emotions = [e.upper() for e in nrc_lexicon.get(w_lower, []) if e not in ('positive', 'negative')]
    if not emotions:
        return None
    priority = ['JOY', 'SADNESS', 'TRUST', 'DISGUST', 'ANTICIPATION', 'SURPRISE', 'FEAR', 'ANGER']
    for p in priority:
        if p in emotions:
            return p
    return emotions[0]

# Calculate word-level statistics using INTRINSIC VADER WORD SCORE for X-axis
word_data = {}
for idx, row in df.iterrows():
    rating = row['rating']
    text = str(row['review_title']) + " " + str(row['review_text'])
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    for token in set(tokens):
        if token in stop_words:
            continue
        cat = map_word_to_nrc_or_cate(token)
        if cat is None:
            continue
        if token not in word_data:
            word_data[token] = {'ratings': [], 'count': 0, 'category': cat}
        word_data[token]['ratings'].append(rating)
        word_data[token]['count'] += 1

records = []
for word, stats in word_data.items():
    if stats['count'] < 15:
        continue
    
    # Calculate INTRINSIC VADER WORD SCORE (-1.0 to +1.0)
    # VADER lexicon scores range from -4.0 to +4.0. Normalize by dividing by 4.0.
    if word in vader_lexicon:
        intrinsic_polarity = vader_lexicon[word] / 4.0
    else:
        # Neutral if word not explicitly in VADER dictionary
        intrinsic_polarity = 0.0
        
    records.append({
        'word': word,
        'count': stats['count'],
        'mean_rating': np.mean(stats['ratings']),
        'intrinsic_polarity': intrinsic_polarity,
        'category': stats['category']
    })

words_df = pd.DataFrame(records)
dataset_mean_rating = df['rating'].mean()

# Save word-level stats to CSV
out_csv = 'data/derived_outputs/nrc_word_level_vader_stats.csv'
words_df.to_csv(out_csv, index=False)
print(f"Saved word-level VADER stats to {out_csv}")

# -------------------------------------------------------------
# Generate Publication Scatter Plot: Intrinsic Word VADER (X) vs Average Rating (Y)
# -------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(15.0, 10.0), dpi=300)

plutchik_legend_order = [
    ('JOY', 'Joy [Pair 1]'),
    ('SADNESS', 'Sadness [Pair 1]'),
    ('TRUST', 'Trust [Pair 2]'),
    ('DISGUST', 'Disgust [Pair 2]'),
    ('ANTICIPATION', 'Anticipation [Pair 3]'),
    ('SURPRISE', 'Surprise [Pair 3]'),
    ('FEAR', 'Fear [Pair 4]'),
    ('ANGER', 'Anger [Pair 4]'),
    ('CATE', 'CATE [Domain Attributes]')
]

for cat_code, cat_label in plutchik_legend_order:
    sub = words_df[words_df['category'] == cat_code]
    if len(sub) == 0:
        continue
    color = PLUTCHIK_COLORS[cat_code]
    sizes = 40 + 34 * np.log10(sub['count'])
    
    z_ord = 4 if cat_code in ['CATE', 'FEAR'] else 3
    lw = 0.8 if cat_code in ['CATE', 'FEAR'] else 0.5
    
    cnt_n = len(sub)
    ax.scatter(
        sub['intrinsic_polarity'], sub['mean_rating'],
        c=color, s=sizes, label=f"{cat_label} (n={cnt_n})",
        alpha=0.92 if cat_code in ['CATE', 'FEAR'] else 0.82, 
        edgecolors='black', linewidths=lw, zorder=z_ord
    )

ax.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.5, zorder=2, label=f'Dataset Mean Rating ({dataset_mean_rating:.2f})')
ax.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2, zorder=2)

# Highlighting genuine English emotion words and friction/cate landmark words
curated_annotate_words = {
    'horrible', 'terrible', 'wasted', 'awful', 'disappointing', 'ruined', 'beware', 'waste', 'refused',
    'uncomfortable', 'delay', 'cancel', 'maintenance', 'lack', 'boring', 'worse',
    'nervous', 'scared', 'fear', 'afraid', 'anxious', 'terrified', 'frightened',
    'pilot', 'captain', 'worth', 'small', 'friendly', 'courteous', 'skilled', 
    'spectacular', 'unbelievable', 'breathtaking', 'epic', 'grandeur', 'priceless', 'safe', 'calm'
}

# ALL WORD LABELS UNIFIED & FIXED IN DARK SLATE BLACK (#1E293B), REGULAR WEIGHT, 8.5pt
texts = []
for idx, row in words_df.iterrows():
    w = row['word']
    if w in curated_annotate_words:
        x = row['intrinsic_polarity']
        y = row['mean_rating']
        
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

ax.set_title('Word Sentiment Scatter Plot: Intrinsic Word VADER Polarity (X) vs Average Tourist Rating (Y)\n[Pure English Filtered Dataset, Plutchik Pairwise Colors, Unified Dark Text Labels]', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Intrinsic Word VADER Sentiment Polarity (-1.0 to +1.0)', fontsize=12, labelpad=10)
ax.set_ylabel('Average Tourist Star Rating (1.0 to 5.0 Stars)', fontsize=12, labelpad=10)

ax.legend(title='Plutchik Emotion Pairs & CATE Domain', fontsize=9.5, title_fontsize=10.5, loc='lower left', frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()
out_dir = 'figures/nrc_emotion_plots'
os.makedirs(out_dir, exist_ok=True)
out_fig = os.path.join(out_dir, 'nrc_word_level_vader_scatter.png')
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.savefig('figures/word_sentiment_scatter_exact_match.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"Saved Intrinsic Word VADER scatter plot to {out_fig}")
