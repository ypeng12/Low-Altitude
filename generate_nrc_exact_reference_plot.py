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
from adjustText import adjust_text

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# 1. Load Master Dataset & 107 Curated CATE Words
master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
cate_path = 'data/derived_outputs/cate_words_curated_107.csv'

print(f"Loading master dataset from {master_path}...")
df = pd.read_csv(master_path)
df_eng = df[df['is_english'] == 1].copy()

# Load 107 CATE words
cate_words_set = set()
if os.path.exists(cate_path):
    cate_df = pd.read_csv(cate_path)
    for w in cate_df['CATE 词汇']:
        word_match = re.match(r'^([a-zA-Z\-]+)', str(w).strip())
        if word_match:
            cate_words_set.add(word_match.group(1).lower())
print(f"Strictly loaded {len(cate_words_set)} user-curated CATE words from {cate_path}.")

# Pre-load Saif Mohammad's Official NRC Word-Emotion Association Lexicon
nrc_lexicon = NRCLex().__lexicon__

stop_words = set(stopwords.words('english'))
stop_words.update({'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'})

# Vivid & Bright Palette with CATE as the brightest Electric Neon Gold (#FFE500)
VIVID_EMOTION_COLORS = {
    'ANTICIPATION': '#FF7F0E',    # Vivid Orange
    'TRUST': '#0284C7',          # Bright Sky Blue
    'JOY': '#22C55E',           # Bright Emerald Green
    'ANGER': '#FF4500',         # Bright Coral Red
    'FEAR': '#E50914',          # Bright Neon Red
    'SADNESS': '#D946EF',       # Bright Magenta Pink
    'DISGUST': '#D97706',       # Bright Amber Brown
    'SURPRISE': '#8B5CF6',      # Vivid Electric Purple
    'CATE': '#FFE500'           # Super Bright Electric Neon Gold (Brightest / Most Important)
}

def map_word_to_nrc_or_cate(word):
    w_lower = word.lower()
    if w_lower in cate_words_set:
        return 'CATE'
    emotions = [e.upper() for e in nrc_lexicon.get(w_lower, []) if e not in ('positive', 'negative')]
    if not emotions:
        return None
    priority = ['ANGER', 'ANTICIPATION', 'DISGUST', 'FEAR', 'JOY', 'SADNESS', 'SURPRISE', 'TRUST']
    for p in priority:
        if p in emotions:
            return p
    return emotions[0]

print("Computing word-level VADER sentiment polarity and star ratings...")
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
        category = map_word_to_nrc_or_cate(token)
        if category is None:
            continue
        if token not in word_data:
            word_data[token] = {'ratings': [], 'polarities': [], 'count': 0, 'category': category}
        word_data[token]['ratings'].append(rating)
        word_data[token]['polarities'].append(polarity)
        word_data[token]['count'] += 1

min_freq = 15
records = []
for word, stats in word_data.items():
    cnt = stats['count']
    if cnt < min_freq:
        continue
    mean_rating = np.mean(stats['ratings'])
    mean_polarity = np.mean(stats['polarities'])
    category = stats['category']
    records.append({
        'word': word,
        'count': cnt,
        'mean_rating': mean_rating,
        'mean_polarity': mean_polarity,
        'category': category
    })

words_df = pd.DataFrame(records)
dataset_mean_rating = df['rating'].mean()

# -------------------------------------------------------------
# Generate Clean Publication Scatter Plot
# Order: NRC Emotions by count, and CATE strictly AT THE END
# -------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(15.0, 10.0), dpi=300)

# Sort NRC emotion categories by count descending, then append CATE AT THE VERY END
nrc_counts = words_df[words_df['category'] != 'CATE']['category'].value_counts()
categories_order = nrc_counts.index.tolist()
categories_order.append('CATE')

for cat in categories_order:
    sub = words_df[words_df['category'] == cat]
    if len(sub) == 0:
        continue
    color = VIVID_EMOTION_COLORS[cat]
    sizes = 40 + 34 * np.log10(sub['count'])
    
    z_ord = 4 if cat == 'CATE' else 3
    lw = 0.8 if cat == 'CATE' else 0.5
    
    cnt_n = len(sub)
    ax.scatter(
        sub['mean_polarity'], sub['mean_rating'],
        c=color, s=sizes, label=f"{cat} (n={cnt_n})",
        alpha=0.92 if cat == 'CATE' else 0.85, 
        edgecolors='black', linewidths=lw, zorder=z_ord
    )

ax.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.5, zorder=2, label=f'Dataset Mean Rating ({dataset_mean_rating:.2f})')
ax.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2, zorder=2)

# Explicit Curated Words List to Annotate
curated_annotate_words = {
    # 1. Upper-Left & Upper-Middle Points Requested by User
    'war', 'dank', 'gut', 'die', 'sin', 'dire', 'genial', 'art', 
    'voyage', 'airs', 'mail', 'fuss', 'worse', 'fall',
    
    # 2. Bottom & Lower-Left Friction Points (Distinct Outliers)
    'horrible', 'terrible', 'wasted', 'awful', 'disappointing', 'ruined', 'beware', 'waste', 'refused',
    
    # 3. Specific Key Service Friction (Clear Outliers)
    'uncomfortable', 'delay', 'cancel', 'maintenance', 'lack', 'boring',
    
    # 4. High-Rating Negative Emotion Landmarks
    'nervous', 'scared', 'fear', 'afraid',
    
    # 5. Top-Right Key Anchor Words
    'pilot', 'captain', 'worth', 'small', 'friendly', 'courteous', 'skilled', 
    'spectacular', 'unbelievable', 'breathtaking', 'epic', 'grandeur', 'priceless', 'safe', 'calm'
}

# Function to get text label color transitioning from bright to dark based on rating & polarity
def get_label_color_brightness(rating, polarity, category):
    if rating >= 4.8:
        # High rating -> Bright Navy / Ocean Blue
        return '#1E3A8A'
    elif rating >= 4.2:
        # Mid-High rating -> Dark Slate Blue
        return '#334155'
    elif rating >= 3.5:
        # Mid-Low rating -> Deep Charcoal / Dark Amber
        return '#4B5563'
    else:
        # Low rating (Severe Friction) -> Deep Crimson Dark Maroon
        return '#881337'

texts = []
for idx, row in words_df.iterrows():
    w = row['word']
    if w in curated_annotate_words:
        x = row['mean_polarity']
        y = row['mean_rating']
        cat = row['category']
        
        txt_color = get_label_color_brightness(y, x, cat)
        fw = 'bold' if y < 3.5 or x < -0.2 else 'normal'
        
        txt = ax.text(x, y, w, fontsize=8.5, fontweight=fw, color=txt_color, alpha=0.95, zorder=5)
        texts.append(txt)

print(f"Annotating exactly {len(texts)} clean curated words with rating-brightness color coding...")

adjust_text(
    texts,
    arrowprops=dict(arrowstyle='->', color='#64748B', lw=0.6, alpha=0.75),
    expand_text=(1.25, 1.35),
    expand_points=(1.25, 1.35),
    force_text=(0.6, 0.9),
    force_points=(0.6, 0.9)
)

ax.set_title('Word Sentiment Scatter Plot: VADER Polarity (X) vs Average Tourist Rating (Y)\n[Text Labels Color-Coded from Bright Navy (High Rating) to Dark Maroon (Friction)]', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Average VADER Sentiment Polarity (-1.0 to +1.0)', fontsize=12, labelpad=10)
ax.set_ylabel('Average Tourist Star Rating (1.0 to 5.0 Stars)', fontsize=12, labelpad=10)

ax.legend(title='Dominant Emotion (CATE at End)', fontsize=10, title_fontsize=11, loc='lower right', frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()

# Save to figures/nrc_emotion_plots/ and figures/
out_dir = 'figures/nrc_emotion_plots'
os.makedirs(out_dir, exist_ok=True)
out_fig = os.path.join(out_dir, 'nrc_8_emotions_vivid_scatter.png')
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.savefig('figures/word_sentiment_scatter_exact_match.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"Saved clean scatter plot to {out_fig}")
