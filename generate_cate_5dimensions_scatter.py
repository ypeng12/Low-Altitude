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

print(f"Loaded {len(cate_words_dict)} user-curated CATE adjectives.")

# 2. Map 107 CATE Words to 5 ServQual & Psychological Dimensions
def assign_5_servqual_dimension(word):
    w = word.lower()
    
    # Dimension 1: Pilot & Operational Expertise (飞行员与服务专业度)
    if w in [
        'pilot', 'captain', 'information', 'knowledge', 'customer', 'personable', 'skilled', 
        'courteous', 'polite', 'working', 'attention', 'contact', 'communicative', 'gracious', 
        'hospitality', 'careful', 'carefully', 'seasoned', 'kindness', 'superior', 'solid', 
        'educated', 'chatty', 'timely', 'stellar', 'graciously', 'courtesy', 'energetic', 'comprehensive'
    ]:
        return 'Pilot & Service Quality'
        
    # Dimension 2: Aerial Scenery & Visual Impact (高空景观与视觉震撼)
    if w in [
        'spectacular', 'unbelievable', 'breathtaking', 'epic', 'grandeur', 'crystal', 'coast', 
        'sky', 'sea', 'rugged', 'hidden', 'diverse', 'immense', 'charm', 'priceless'
    ]:
        return 'Aerial Scenery & Environment'
        
    # Dimension 3: Cabin Facilities & Flight Dynamics (机舱设施与飞行舒适度)
    if w in [
        'small', 'ease', 'completely', 'calm', 'organized', 'sense', 'cold', 'noise', 
        'actual', 'inaccessible', 'spirit', 'balance', 'silk', 'balanced', 'leisurely'
    ]:
        return 'Cabin Facilities & Comfort'
        
    # Dimension 4: Perceived Value & Booking Flexibility (产品价值与预订自由度)
    if w in [
        'worth', 'extra', 'choice', 'cheap', 'strongly', 'fair', 'flexibility', 'decent', 
        'inexpensive', 'valuable', 'essential', 'afford', 'advantage'
    ]:
        return 'Perceived Value & Flexibility'
        
    # Dimension 5: Psychological Thrill & Friction/Emotion Shift (心理惊险与服务摩擦)
    return 'Psychological Thrill & Service Friction'

# 3. Calculate word-level statistics from master reviews
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
        dim = assign_5_servqual_dimension(word)
        records.append({
            'word': word,
            'raw_label': cate_words_dict[word],
            'count': stats['count'],
            'mean_rating': mean_rating,
            'raw_vader_score': raw_vader,
            'dimension': dim
        })

cate_result_df = pd.DataFrame(records)
dataset_mean_rating = df['rating'].mean()

# Save stats to derived_outputs
out_csv = 'data/derived_outputs/cate_5dimensions_words_stats.csv'
cate_result_df.to_csv(out_csv, index=False, encoding='utf-8-sig')
print(f"Saved 5-Dimension CATE stats to {out_csv}")

# 4. Plot 5-Dimension Scatter Plot
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(15.0, 10.0), dpi=300)

DIMENSION_COLORS = {
    'Pilot & Service Quality': '#0284C7',                  # Vivid Sky Blue
    'Aerial Scenery & Environment': '#22C55E',              # Emerald Green
    'Cabin Facilities & Comfort': '#8B5CF6',                # Vivid Electric Purple
    'Perceived Value & Flexibility': '#F59E0B',             # Warm Gold Orange
    'Psychological Thrill & Service Friction': '#E50914'    # Crimson Red
}

dimensions_order = [
    'Pilot & Service Quality',
    'Aerial Scenery & Environment',
    'Cabin Facilities & Comfort',
    'Perceived Value & Flexibility',
    'Psychological Thrill & Service Friction'
]

for dim in dimensions_order:
    sub = cate_result_df[cate_result_df['dimension'] == dim]
    if len(sub) == 0:
        continue
    color = DIMENSION_COLORS[dim]
    sizes = 45 + 36 * np.log10(sub['count'])
    
    cnt_n = len(sub)
    ax.scatter(
        sub['raw_vader_score'], sub['mean_rating'],
        c=color, s=sizes, label=f"{dim} (n={cnt_n})",
        alpha=0.88, edgecolors='black', linewidths=0.7, zorder=3
    )

ax.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.5, zorder=2, label=f'Dataset Mean Rating ({dataset_mean_rating:.2f})')
ax.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2, zorder=2)

# Select landmark words to annotate across all 5 dimensions cleanly
texts = []
annotate_words = {
    'worth', 'small', 'skilled', 'courteous', 'unbelievable', 'spectacular', 
    'breathtaking', 'calm', 'cold', 'loud', 'cheap', 'priceless', 'extra', 
    'wrong', 'uncomfortable', 'lack', 'boring', 'delayed', 'cramped', 'personable', 'epic'
}

for idx, row in cate_result_df.iterrows():
    w = row['word']
    x = row['raw_vader_score']
    y = row['mean_rating']
    
    if w in annotate_words or x < -0.5 or y < 4.6:
        txt = ax.text(x, y, w, fontsize=8.5, fontweight='normal', color='#1E293B', alpha=0.95, zorder=5)
        texts.append(txt)

adjust_text(
    texts,
    arrowprops=dict(arrowstyle='->', color='#64748B', lw=0.6, alpha=0.75),
    expand_text=(1.2, 1.3),
    expand_points=(1.2, 1.3),
    force_text=(0.5, 0.8),
    force_points=(0.5, 0.8)
)

ax.set_title('CATE 107 Domain Keywords: 5 ServQual & Psychological Experience Dimensions\n[Raw VADER Word Score (-4.0 to +4.0) vs Average Tourist Rating (1.0 to 5.0)]', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Raw Inherent VADER Word Polarity Score (-4.0 to +4.0 Scale)', fontsize=12, labelpad=10)
ax.set_ylabel('Average Tourist Star Rating (1.0 to 5.0 Stars)', fontsize=12, labelpad=10)
ax.set_xlim(-4.0, +4.0)

ax.legend(title='CATE 5 Experience Dimensions', fontsize=10, title_fontsize=11, loc='lower left', frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()
out_dir = 'figures/cate_sentiment_plots'
os.makedirs(out_dir, exist_ok=True)
out_fig = os.path.join(out_dir, 'cate_5dimensions_scatter.png')
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()

print(f"Saved 5-Dimension CATE scatter plot to {out_fig}")
