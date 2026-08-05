import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import sys
from nrclex import NRCLex
from nltk.corpus import stopwords, words as nltk_english_words
import nltk
from adjustText import adjust_text

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure NLTK words corpus is available
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words', quiet=True)

# 1. Load Master Dataset
master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
cate_path = 'data/derived_outputs/cate_words_full_224.csv'

print(f"Loading master dataset from {master_path}...")
df = pd.read_csv(master_path)

# Filter English reviews (N=21,238)
df_eng = df[df['is_english'] == 1].copy()
print(f"Filtered English reviews: {len(df_eng)} rows.")

# Build valid English vocabulary set
english_vocab = set(w.lower() for w in nltk_english_words.words())
domain_places = {'kauai', 'napali', 'denali', 'talkeetna', 'vegas', 'maui', 'oahu', 'alaska', 'hawaii', 'canyon', 'waimea', 'gorge'}
english_vocab.update(domain_places)

# Load CATE domain words
cate_words_set = set()
if os.path.exists(cate_path):
    cate_df = pd.read_csv(cate_path)
    for w in cate_df['CATE 词汇']:
        word_match = re.match(r'^([a-zA-Z\-]+)', str(w).strip())
        if word_match:
            word_clean = word_match.group(1).lower()
            cate_words_set.add(word_clean)
            english_vocab.add(word_clean)
print(f"Loaded {len(cate_words_set)} CATE domain words.")

# Pre-load Saif Mohammad's Official NRC Word-Emotion Association Lexicon
nrc_lexicon = NRCLex().__lexicon__

stop_words = set(stopwords.words('english'))
basic_stops = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}
stop_words.update(basic_stops)

# 8 Official NRC Emotion Categories (Plutchik's Model) + CATE Domain Feature
NRC_COLORS = {
    'CATE Domain Feature': '#F59E0B',   # Warm Amber / Gold
    'Anger': '#DC2626',                  # Crimson Red
    'Anticipation': '#EA580C',            # Bright Orange
    'Disgust': '#78350F',                # Deep Brown
    'Fear': '#BE185D',                   # Dark Rose / Magenta
    'Joy': '#16A34A',                    # Emerald Green
    'Sadness': '#7C3AED',                # Violet Purple
    'Surprise': '#0D9488',               # Teal / Cyan
    'Trust': '#2563EB'                   # Royal Blue
}

def get_official_nrc_category(word):
    w_lower = word.lower()
    
    # Priority 1: CATE Low-Altitude Domain Feature
    if w_lower in cate_words_set or w_lower in ['pilot', 'captain', 'safety', 'weather', 'canyon', 'glacier', 'coast', 'waterfall', 'helicopter', 'chopper', 'plane', 'price', 'worth', 'staff', 'flight', 'tour', 'view', 'scenery', 'seats', 'window']:
        return 'CATE Domain Feature'
    
    # Priority 2: Saif Mohammad's 8 NRC Basic Emotions
    emotions = [e.capitalize() for e in nrc_lexicon.get(w_lower, []) if e not in ('positive', 'negative')]
    
    if not emotions:
        return 'Trust'  # Default fallback
    
    priority = ['Anger', 'Disgust', 'Fear', 'Sadness', 'Surprise', 'Anticipation', 'Joy', 'Trust']
    for p in priority:
        if p in emotions:
            return p
    return emotions[0]

print("Computing word-level VADER sentiment polarity and star ratings...")
word_data = {}
for idx, row in df_eng.iterrows():
    rating = row['rating']
    polarity = row['sentiment_polarity']
    text = str(row['review_title']) + " " + str(row['review_text'])
    
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    unique_tokens = set(tokens)
    
    for token in unique_tokens:
        if token in stop_words:
            continue
        if token not in english_vocab and token not in nrc_lexicon:
            continue
        if token not in word_data:
            word_data[token] = {'ratings': [], 'polarities': [], 'count': 0}
        word_data[token]['ratings'].append(rating)
        word_data[token]['polarities'].append(polarity)
        word_data[token]['count'] += 1

min_freq = 25
records = []
for word, stats in word_data.items():
    cnt = stats['count']
    if cnt < min_freq:
        continue
    mean_rating = np.mean(stats['ratings'])
    mean_polarity = np.mean(stats['polarities'])
    
    if mean_polarity < 0.0 and word not in ['not', 'no', 'never', 'bad', 'poor', 'sad', 'hate', 'fear', 'sick', 'die', 'war', 'dire', 'sin', 'grim']:
        continue
        
    category = get_official_nrc_category(word)
    
    records.append({
        'word': word,
        'count': cnt,
        'mean_rating': mean_rating,
        'mean_polarity': mean_polarity,
        'category': category
    })

words_df = pd.DataFrame(records)
dataset_mean_rating = df_eng['rating'].mean()
print(f"Computed statistics for {len(words_df)} English keywords classified across 8 NRC emotions + CATE.")

# -------------------------------------------------------------
# Generate Publication-Grade Scatter Plot V2
# -------------------------------------------------------------
plt.style.use('seaborn-v0_8-white' if 'seaborn-v0_8-white' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(14, 8.8), dpi=300)

ax.set_facecolor('#F8F9FA')
ax.grid(True, linestyle='--', color='#E2E8F0', alpha=0.7, zorder=1)

# Plot Points Layer by Layer for 8 NRC Emotions + CATE Domain Feature
plot_categories = ['CATE Domain Feature', 'Joy', 'Trust', 'Anticipation', 'Surprise', 'Fear', 'Sadness', 'Disgust', 'Anger']

for cat in plot_categories:
    sub = words_df[words_df['category'] == cat]
    if len(sub) == 0:
        continue
    color = NRC_COLORS[cat]
    sizes = 30 + 32 * np.log10(sub['count'])
    
    ax.scatter(
        sub['mean_polarity'], sub['mean_rating'],
        c=color, s=sizes, label=f"{cat} (n={len(sub)})",
        alpha=0.82, edgecolors='white', linewidths=0.5, zorder=3
    )

# Reference Lines
ax.axhline(dataset_mean_rating, color='#64748B', linestyle=':', linewidth=1.5, zorder=2)
ax.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2, zorder=2)

# Theoretical Quadrant Annotation Boxes (POSITIONED TO NEVER OVERLAP WITH LEGEND)
ax.text(-0.72, 4.97, 'Quadrant II: Risk Perception & Reassurance\n(High Rating, Perceived Risk Mention)', 
        fontsize=9.5, fontweight='bold', color='#334155', alpha=0.65, va='top')
ax.text(0.72, 4.97, 'Quadrant I: Core Satisfaction & Delight\n(High Rating, High Sentiment Polarity)', 
        fontsize=9.5, fontweight='bold', color='#15803D', alpha=0.75, va='top')
ax.text(-0.72, 2.40, 'Quadrant III: Severe Service Failure\n(Low Rating, Dissatisfaction)', 
        fontsize=9.5, fontweight='bold', color='#B91C1C', alpha=0.70, va='bottom')
ax.text(0.18, 2.40, 'Quadrant IV: Friction & Value Deficit\n(Low Rating, Operational Complaints)', 
        fontsize=9.5, fontweight='bold', color='#C2410C', alpha=0.70, va='bottom')

# Curated Representative Domain & NRC Emotion Keywords to Annotate
key_words_to_annotate = [
    # Dissatisfaction / Pain Points (Quadrant III & IV)
    'horrible', 'terrible', 'wasted', 'rude', 'disappointing', 'worst', 'uncomfortable', 
    'delay', 'cancel', 'refund', 'maintenance', 'lack', 'waste', 'bother',
    # Risk Perception / Safety (Quadrant II & I)
    'safety', 'safe', 'scared', 'nervous', 'calm', 'smooth',
    # Pilot & Service Touchpoints (Quadrant I)
    'pilot', 'captain', 'knowledge', 'friendly', 'courteous', 'skilled',
    # Value & Scenery (Quadrant I)
    'canyon', 'glacier', 'waterfall', 'coast', 'spectacular', 'unbelievable', 'worth', 'breathtaking'
]

texts = []
annotated_set = set()

for idx, row in words_df.iterrows():
    w = row['word']
    x = row['mean_polarity']
    y = row['mean_rating']
    
    if w in key_words_to_annotate:
        if w not in annotated_set:
            txt = ax.text(
                x, y, w, fontsize=8.5, fontweight='bold', color='#0F172A', zorder=5
            )
            texts.append(txt)
            annotated_set.add(w)

print(f"Applying adjustText to format {len(texts)} clear labels...")
adjust_text(
    texts,
    arrowprops=dict(arrowstyle='-', color='#64748B', lw=0.6, alpha=0.7),
    expand_text=(1.2, 1.3),
    expand_points=(1.2, 1.3),
    force_text=(0.4, 0.6),
    force_points=(0.2, 0.4),
    ax=ax
)

ax.set_title('Figure X: Semantic Distribution of Low-Altitude Tourism Keywords Across Saif Mohammad\'s 8 NRC Basic Emotions', 
             fontsize=12, fontweight='bold', pad=15, color='#0F172A')
ax.set_xlabel('Average VADER Sentiment Polarity of Reviews Containing Keyword (-1.0 to +1.0)', fontsize=10, fontweight='bold', labelpad=8)
ax.set_ylabel('Average Tourist Star Rating (1.0 to 5.0 Stars)', fontsize=10, fontweight='bold', labelpad=8)

ax.text(0.98, dataset_mean_rating + 0.03, f'Mean Rating = {dataset_mean_rating:.2f}', 
        color='#64748B', fontsize=8.5, fontweight='bold', ha='right', va='bottom')

# Clean Legend in Bottom Right (Strict 8 NRC Emotions + CATE)
ax.legend(
    title='Saif Mohammad\'s 8 NRC Emotions + CATE', 
    loc='lower right', 
    frameon=True, 
    facecolor='white', 
    edgecolor='#CBD5E1', 
    fontsize=8.5, 
    title_fontsize=9.5
)

ax.set_xlim(-0.75, 1.02)
ax.set_ylim(2.20, 5.08)

plt.tight_layout()
output_path = 'figures/nrc_8_emotions_word_scatter_v2.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Publication-ready 8-NRC emotion scatter plot v2 saved to {output_path}")
