import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import sys
from nrclex import NRCLex
from nltk.corpus import stopwords
import nltk

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure NLTK stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# 1. Load Dataset
data_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
print(f"Loading master dataset from {data_path}...")
df = pd.read_csv(data_path)

# Load CATE words
cate_csv_path = 'data/derived_outputs/cate_words_full_224.csv'
cate_words_set = set()
if os.path.exists(cate_csv_path):
    cate_df = pd.read_csv(cate_csv_path)
    for w in cate_df['CATE 词汇']:
        word_match = re.match(r'^([a-zA-Z\-]+)', str(w).strip())
        if word_match:
            cate_words_set.add(word_match.group(1).lower())
print(f"Loaded {len(cate_words_set)} CATE domain words.")

# 2. Extract Vocabulary & Compute Word-level Stats
stop_words = set(stopwords.words('english'))
basic_stops = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}
stop_words.update(basic_stops)

# Pre-load NRC Lexicon dictionary
nrc_lexicon = NRCLex().__lexicon__

EMOTION_COLORS = {
    'CATE': '#F1C40F',          # Bright Yellow / Gold
    'ANGER': '#7F8C8D',         # Grey / Dark Slate
    'ANTICIPATION': '#E67E22',    # Orange
    'DISGUST': '#8D6E63',       # Brown
    'FEAR': '#E74C3C',          # Red
    'JOY': '#2ECC71',           # Green
    'SADNESS': '#E91E63',       # Pink
    'SURPRISE': '#9B59B6',      # Purple
    'TRUST': '#3498DB'          # Blue
}

def get_word_nrc_category(word):
    w_lower = word.lower()
    if w_lower in cate_words_set:
        return 'CATE'
    
    emotions = nrc_lexicon.get(w_lower, [])
    discrete_emotions = [e.upper() for e in emotions if e not in ('positive', 'negative')]
    
    if not discrete_emotions:
        return 'TRUST'  # default fallback if unclassified
    
    # Emotion priority: ANGER/DISGUST/FEAR/SADNESS > JOY/TRUST/ANTICIPATION/SURPRISE
    priority_order = ['ANGER', 'DISGUST', 'FEAR', 'SADNESS', 'JOY', 'TRUST', 'ANTICIPATION', 'SURPRISE']
    for p in priority_order:
        if p in discrete_emotions:
            return p
    return discrete_emotions[0]

print("Processing reviews to compute word-level VADER polarity and Star Ratings...")

word_data = {}

for idx, row in df.iterrows():
    rating = row['rating']
    polarity = row['sentiment_polarity']
    text = str(row['review_title']) + " " + str(row['review_text'])
    
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    unique_tokens = set(tokens)
    
    for token in unique_tokens:
        if token in stop_words:
            continue
        if token not in word_data:
            word_data[token] = {'ratings': [], 'polarities': [], 'count': 0}
        word_data[token]['ratings'].append(rating)
        word_data[token]['polarities'].append(polarity)
        word_data[token]['count'] += 1

print(f"Total unique words extracted: {len(word_data)}")

min_freq = 15
records = []

for word, stats in word_data.items():
    cnt = stats['count']
    if cnt < min_freq:
        continue
    mean_rating = np.mean(stats['ratings'])
    mean_polarity = np.mean(stats['polarities'])
    category = get_word_nrc_category(word)
    
    records.append({
        'word': word,
        'count': cnt,
        'mean_rating': mean_rating,
        'mean_polarity': mean_polarity,
        'category': category
    })

words_df = pd.DataFrame(records)
print(f"Filtered {len(words_df)} high-frequency words (min_freq={min_freq}).")

dataset_mean_rating = df['rating'].mean()

# -------------------------------------------------------------
# PLOT 1: Single Panel Scatter Plot
# -------------------------------------------------------------
print("Generating Single Panel Word Sentiment Scatter Plot...")

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(14, 10), dpi=300)

categories = ['CATE', 'ANGER', 'ANTICIPATION', 'DISGUST', 'FEAR', 'JOY', 'SADNESS', 'SURPRISE', 'TRUST']

for cat in categories:
    sub = words_df[words_df['category'] == cat]
    if len(sub) == 0:
        continue
    color = EMOTION_COLORS[cat]
    sizes = np.clip(np.sqrt(sub['count']) * 4, 30, 200)
    ax.scatter(sub['mean_polarity'], sub['mean_rating'], c=color, s=sizes, 
               label=f"{cat} (n={len(sub)})", alpha=0.8, edgecolors='black', linewidths=0.5)

ax.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.2, label=f'Dataset Mean Rating ({dataset_mean_rating:.2f})')
ax.axvline(0.0, color='gray', linestyle='--', linewidth=1.0)

words_to_annotate = [
    'dank', 'war', 'sin', 'die', 'gut', 'dire', 'genial', 'voyage', 'airs', 'art', 
    'horrible', 'wasted', 'refused', 'disappointing', 'terrible', 'worse', 'boring', 
    'inform', 'upset', 'lack', 'maintenance', 'hurry', 'management', 'money', 
    'pilot', 'uncourtious', 'ruin', 'mistake', 'complain', 'dangerous', 'uncomfortable',
    'delay', 'bank', 'credit', 'decent', 'ground', 'memorable', 'spectacular', 'experienced',
    'unique', 'perfect', 'beauty', 'special'
]

annotated = set()
for idx, row in words_df.iterrows():
    w = row['word']
    x = row['mean_polarity']
    y = row['mean_rating']
    
    if w in words_to_annotate or x < 0.4 or y < 4.2 or y > 4.96:
        if w not in annotated:
            ax.annotate(w, (x, y), fontsize=8.5, fontweight='bold', alpha=0.85, 
                        xytext=(3, 3), textcoords='offset points')
            annotated.add(w)

ax.set_title('Word Sentiment Scatter Plot: VADER Polarity (X) vs Average Tourist Rating (Y)', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Average VADER Sentiment Polarity of Reviews Containing Word (-1.0 to +1.0)', fontsize=11, fontweight='bold')
ax.set_ylabel('Average Tourist Star Rating (1.0 to 5.0 Stars)', fontsize=11, fontweight='bold')
ax.legend(title='Dominant NRC Emotion (CATE = Bright Yellow)', loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9)
plt.tight_layout()

single_plot_path = 'figures/word_sentiment_scatter_single.png'
plt.savefig(single_plot_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved single panel plot to {single_plot_path}")

# -------------------------------------------------------------
# PLOT 2: Two-Panel Overview + Zoomed Detail Scatter Plot
# -------------------------------------------------------------
print("Generating Two-Panel Word Sentiment Scatter Plot...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), dpi=300)
fig.suptitle('Word Sentiment Scatter Plot: Global Overview (Left) + Zoomed Top-Right Detail (Right)', fontsize=16, fontweight='bold', y=0.98)

# Panel A: Global Overview
for cat in categories:
    sub = words_df[words_df['category'] == cat]
    if len(sub) == 0:
        continue
    color = EMOTION_COLORS[cat]
    sizes = np.clip(np.sqrt(sub['count']) * 3.5, 25, 180)
    ax1.scatter(sub['mean_polarity'], sub['mean_rating'], c=color, s=sizes, 
                label=f"{cat} (n={len(sub)})", alpha=0.8, edgecolors='black', linewidths=0.4)

ax1.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.2)
ax1.axvline(0.0, color='gray', linestyle='--', linewidth=1.0)

rect_x = [0.48, 1.00, 1.00, 0.48, 0.48]
rect_y = [4.58, 4.58, 5.02, 5.02, 4.58]
ax1.plot(rect_x, rect_y, color='magenta', linestyle='--', linewidth=1.8)
ax1.text(0.49, 4.50, 'Zoomed Region (Panel B)', color='magenta', fontweight='bold', fontsize=10)

for idx, row in words_df.iterrows():
    w = row['word']
    x = row['mean_polarity']
    y = row['mean_rating']
    if x < 0.45 or y < 4.55 or w in ['voyage', 'dank', 'war', 'dire', 'sin', 'die', 'gut']:
        ax1.annotate(w, (x, y), fontsize=8, alpha=0.85, xytext=(2, 2), textcoords='offset points')

ax1.set_title('Panel A: Global Overview (All Quadrants, Top-Left & Bottom Labeled)', fontsize=12, fontweight='bold', color='#2C3E50')
ax1.set_xlabel('VADER Sentiment Polarity (-1.0 to +1.0)', fontsize=10, fontweight='bold')
ax1.set_ylabel('Average Star Rating (1.0 to 5.0 Stars)', fontsize=10, fontweight='bold')
ax1.legend(title='Category (CATE = Bright Yellow)', loc='lower left', fontsize=8)

# Panel B: Zoomed Top-Right Detail
top_right_df = words_df[(words_df['mean_polarity'] >= 0.48) & (words_df['mean_rating'] >= 4.58)]

for cat in categories:
    sub = top_right_df[top_right_df['category'] == cat]
    if len(sub) == 0:
        continue
    color = EMOTION_COLORS[cat]
    sizes = np.clip(np.sqrt(sub['count']) * 4.5, 30, 220)
    ax2.scatter(sub['mean_polarity'], sub['mean_rating'], c=color, s=sizes, 
                label=f"{cat} (n={len(sub)})", alpha=0.8, edgecolors='black', linewidths=0.5)

ax2.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.2)
ax2.set_xlim(0.48, 1.01)
ax2.set_ylim(4.57, 5.03)

for idx, row in top_right_df.iterrows():
    w = row['word']
    x = row['mean_polarity']
    y = row['mean_rating']
    if row['category'] == 'CATE' or row['count'] > 100 or y > 4.90 or y < 4.65 or x > 0.85:
        ax2.annotate(w, (x, y), fontsize=7.5, alpha=0.85, xytext=(2, 2), textcoords='offset points')

ax2.set_title('Panel B: Zoomed Top-Right Detail (Decompressed Cluster)', fontsize=12, fontweight='bold', color='purple')
ax2.set_xlabel('VADER Sentiment Polarity (0.48 to 1.00)', fontsize=10, fontweight='bold')
ax2.set_ylabel('Average Star Rating (4.58 to 5.00 Stars)', fontsize=10, fontweight='bold')
ax2.legend(title='Top-Right Category', loc='lower right', fontsize=8)

plt.tight_layout()
two_panel_plot_path = 'figures/word_sentiment_scatter_two_panel.png'
plt.savefig(two_panel_plot_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved two-panel plot to {two_panel_plot_path}")

print("Scatter plot generation complete successfully!")
