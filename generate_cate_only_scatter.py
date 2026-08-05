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

# 1. Load Master Dataset and 122 CATE Adjective words
master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
cate_path = 'data/derived_outputs/cate_words_adjectives_122.csv'

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

print(f"Loaded {len(cate_words_dict)} valid CATE words.")

# Function to map CATE words into 6 High-Level English Dimensions
def assign_high_level_dimension(word, orig_cat):
    w = word.lower()
    
    # 1. Negative / Friction
    if w in ['wrong', 'uncomfortable', 'lack', 'boring', 'suffer', 'chilly', 'delayed', 'bother', 'cramped']:
        return 'Friction & Service Defects'
    
    # 2. Pilot & Service Quality
    if w in ['job', 'information', 'knowledge', 'captain', 'customer', 'personable', 'skilled', 'courteous', 
            'polite', 'working', 'attention', 'contact', 'communicative', 'gracious', 'hospitality', 
            'culture', 'careful', 'carefully', 'seasoned', 'kindness', 'superior', 'solid', 'educated', 
            'chatty', 'timely', 'stellar', 'graciously', 'courtesy', 'energetic', 'comprehensive']:
        return 'Pilot & Service Quality'
    
    # 3. Value & Booking
    if w in ['worth', 'extra', 'choice', 'cheap', 'strongly', 'fair', 'flexibility', 'decent', 'stress', 
            'inexpensive', 'valuable', 'essential', 'afford', 'priceless', 'advantage', 'effort']:
        return 'Value & Booking Assurance'
        
    # 4. Flight & Cabin Comfort
    if w in ['small', 'ease', 'completely', 'unbelievable', 'calm', 'organized', 'sense', 'cold', 'noise', 
            'standing', 'actual', 'inaccessible', 'spirit', 'balance', 'silk', 'balanced', 'leisurely']:
        return 'Cabin Facilities & Flight Comfort'
        
    # 5. Scenery & Viewpoint
    if w in ['coast', 'sky', 'sea', 'crystal', 'grandeur', 'rugged', 'hidden', 'diverse', 'immense', 'charm']:
        return 'Aerial Scenery & Environment'
    
    # 6. Experience & Emotion (Default for remaining delight words)
    return 'Tourist Delight & Emotional Memory'

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

records = []
for word, stats in word_stats.items():
    if stats['count'] == 0:
        continue
    dim = assign_high_level_dimension(word, cate_words_dict[word]['original_cate'])
    records.append({
        'word': word,
        'raw_label': cate_words_dict[word]['raw'],
        'count': stats['count'],
        'mean_rating': np.mean(stats['ratings']),
        'mean_polarity': np.mean(stats['polarities']),
        'dimension': dim
    })

cate_result_df = pd.DataFrame(records)
print(f"Generated stats for {len(cate_result_df)} CATE words.")
print(cate_result_df['dimension'].value_counts())

# Save to CSV
cate_result_df.to_csv('data/derived_outputs/cate_only_words_stats.csv', index=False)

# -------------------------------------------------------------
# Generate Publication-Grade CATE Standalone Scatter Plot
# -------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(13.5, 8.8), dpi=300)

DIMENSION_COLORS = {
    'Pilot & Service Quality': '#1F77B4',             # Blue
    'Tourist Delight & Emotional Memory': '#2CA02C',   # Green
    'Cabin Facilities & Flight Comfort': '#FF7F0E',    # Orange
    'Value & Booking Assurance': '#9467BD',           # Purple
    'Aerial Scenery & Environment': '#17BECF',        # Cyan
    'Friction & Service Defects': '#D62728'            # Red
}

dim_counts = cate_result_df['dimension'].value_counts()
dims_order = dim_counts.index.tolist()

for dim in dims_order:
    sub = cate_result_df[cate_result_df['dimension'] == dim]
    if len(sub) == 0:
        continue
    color = DIMENSION_COLORS.get(dim, '#7F7F7F')
    sizes = 45 + 38 * np.log10(sub['count'])
    
    ax.scatter(
        sub['mean_polarity'], sub['mean_rating'],
        c=color, s=sizes, label=f"{dim} (n={len(sub)})",
        alpha=0.85, edgecolors='black', linewidths=0.6, zorder=3
    )

dataset_mean_rating = df['rating'].mean()
ax.axhline(dataset_mean_rating, color='red', linestyle=':', linewidth=1.5, zorder=2, label=f'Dataset Mean Rating ({dataset_mean_rating:.2f})')
ax.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2, zorder=2)

# Select key words to annotate clearly
texts = []
annotate_words = [
    'worth', 'small', 'job', 'information', 'coast', 'interesting', 'knowledge', 
    'cool', 'forget', 'captain', 'sky', 'extra', 'sea', 'ease', 'personable', 
    'unbelievable', 'calm', 'skilled', 'courteous', 'organized', 'superb', 
    'noise', 'cheap', 'wrong', 'strongly', 'polite', 'crystal', 'grandeur', 
    'extraordinary', 'hospitality', 'uncomfortable', 'lack', 'boring', 'flexibility', 
    'priceless', 'seasoned', 'adventurous', 'timely', 'diverse'
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

ax.set_title('Standalone CATE Keyword Sentiment Scatter Plot: VADER Polarity (X) vs Tourist Rating (Y)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Average VADER Sentiment Polarity (-1.0 to +1.0)', fontsize=12, labelpad=10)
ax.set_ylabel('Average Tourist Star Rating (1.0 to 5.0 Stars)', fontsize=12, labelpad=10)

ax.legend(title='CATE Semantic Dimensions', fontsize=10, title_fontsize=11, loc='lower right', frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()
os.makedirs('figures', exist_ok=True)
out_fig = 'figures/cate_only_words_scatter.png'
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved standalone CATE scatter plot to {out_fig}")
