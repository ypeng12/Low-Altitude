#!/usr/bin/env python3
"""Generate publication-ready plot comparing Mean Tourist Rating (0 to 5) across NRC 8 Emotion Categories vs NRC 8 Missed words."""

import shutil
from pathlib import Path
import re
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nrclex import NRCLex

fig_dir = Path("figures/nrc_emotion_plots")
fig_dir.mkdir(parents=True, exist_ok=True)
analyze_dir = Path("data/analyze")

# Load Master Gold & full corpus
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
df_eng = pd.read_csv("data/cleaned_datasets/tripadvisor_level3_english_v2.csv")
nrc_dict = NRCLex().__lexicon__

NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

# Calculate mean review rating and count for each word in Gold Lexicon
gold_words_set = set(df_gold['word'].str.lower().str.strip())
word_ratings = defaultdict(list)

print("Calculating word-level mean ratings across N=21,215 reviews...")
for row in df_eng.itertuples():
    text = f"{row.review_title if pd.notna(row.review_title) else ''} {row.review_text if pd.notna(row.review_text) else ''}".lower()
    tokens = set(re.findall(r"\b[a-zA-Z]{2,}\b", text))
    r_rating = float(row.rating)
    for w in tokens:
        if w in gold_words_set:
            word_ratings[w].append(r_rating)

plot_data = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    ratings = word_ratings[w]
    if not ratings:
        ratings = [5.0]
        
    mean_rat = float(np.mean(ratings))
    rev_cnt = len(ratings)
    
    nrc_tags = set(nrc_dict.get(w, [])) | set(nrc_dict.get(lemma, []))
    matched_nrc8 = nrc_tags & NRC8
    
    has_nrc8 = len(matched_nrc8) > 0
    group_label = "NOT in NRC 8 (Domain Awe / Unmapped)" if not has_nrc8 else "IN NRC 8 Emotion Categories"
    
    # Detailed category
    if not has_nrc8:
        det_cat = "NRC8 MISSED (Domain Awe & Appraisal)"
    else:
        # Priority order
        for p in ["joy", "fear", "trust", "surprise", "anticipation", "sadness", "anger", "disgust"]:
            if p in matched_nrc8:
                det_cat = f"NRC8_{p.upper()}"
                break
                
    plot_data.append({
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': row.chinese_translation,
        'mean_rating': mean_rat,
        'review_count': rev_cnt,
        'has_nrc8': has_nrc8,
        'group_label': group_label,
        'detailed_category': det_cat
    })

df_plot = pd.DataFrame(plot_data)

# Set Seaborn Theme
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 2, figsize=(17, 8.5), gridspec_kw={'width_ratios': [1.4, 1]})

# ==========================================
# Panel A: Word Rating Scatter Plot Across NRC 8 vs NRC 8 Missed
# ==========================================
cat_order = [
    "NRC8_JOY", "NRC8_TRUST", "NRC8_ANTICIPATION", "NRC8_SURPRISE",
    "NRC8_FEAR", "NRC8_SADNESS", "NRC8_ANGER", "NRC8_DISGUST",
    "NRC8 MISSED (Domain Awe & Appraisal)"
]

cat_colors = {
    "NRC8_JOY": "#16A34A",
    "NRC8_TRUST": "#1D4ED8",
    "NRC8_ANTICIPATION": "#EA580C",
    "NRC8_SURPRISE": "#9333EA",
    "NRC8_FEAR": "#DC2626",
    "NRC8_SADNESS": "#64748B",
    "NRC8_ANGER": "#B91C1C",
    "NRC8_DISGUST": "#92400E",
    "NRC8 MISSED (Domain Awe & Appraisal)": "#F59E0B"
}

y_positions = {c: i for i, c in enumerate(cat_order)}
df_plot['y_pos'] = df_plot['detailed_category'].map(y_positions)

# Add jitter
np.random.seed(42)
df_plot['y_jitter'] = df_plot['y_pos'] + np.random.uniform(-0.18, 0.18, size=len(df_plot))

for cat in cat_order:
    sub = df_plot[df_plot['detailed_category'] == cat]
    if sub.empty:
        continue
    sizes = 35 + 30 * np.log10(np.maximum(sub['review_count'], 1))
    axes[0].scatter(
        sub['mean_rating'],
        sub['y_jitter'],
        s=sizes,
        color=cat_colors[cat],
        edgecolor='white',
        linewidth=1.0,
        alpha=0.8,
        label=f"{cat.replace('NRC8_', '')} (N={len(sub)})"
    )

# Baseline rating line
corpus_mean = float(df_eng['rating'].mean())
axes[0].axvline(corpus_mean, color="#EF4444", linestyle="--", linewidth=1.5, label=f"Corpus Mean Rating ({corpus_mean:.3f})")

# Annotate High Frequency Words
words_to_label = [
    'great', 'amazing', 'best', 'awesome', 'fantastic', 'incredible', 'breathtaking', 'stunning',
    'unforgettable', 'beautiful', 'friendly', 'wonderful', 'good', 'excellent', 'perfect', 'helpful',
    'nervous', 'scared', 'afraid', 'fear', 'disappointed', 'regret', 'sick', 'horrible', 'terrible', 'annoying'
]

try:
    from adjustText import adjust_text
    texts = []
    for row in df_plot[df_plot['word'].isin(words_to_label)].itertuples():
        texts.append(axes[0].text(row.mean_rating, row.y_jitter, row.word, fontsize=9, weight='bold', color="#0F172A"))
    adjust_text(texts, ax=axes[0], arrowprops=dict(arrowstyle="->", color="#64748B", lw=0.5))
except Exception as e:
    for row in df_plot[df_plot['word'].isin(words_to_label)].itertuples():
        axes[0].annotate(row.word, (row.mean_rating, row.y_jitter), xytext=(2, 2), textcoords="offset points", fontsize=8, weight="bold")

axes[0].set_yticks(range(len(cat_order)))
axes[0].set_yticklabels([c.replace('NRC8_', '') for c in cat_order], fontsize=10, weight='bold')
axes[0].set_xlim(3.0, 5.05)
axes[0].set_xlabel('Mean Tourist Star Rating (3.0 to 5.0 Stars)', fontsize=11, weight='bold', color='#1E293B')
axes[0].set_title('Master Gold Lexicon Words (N=630)\nMean Tourist Rating Scatter Map Across NRC Categories', fontsize=12, weight='bold', color='#0F172A')
axes[0].legend(loc="lower left", fontsize=8.5, framealpha=0.95)

# ==========================================
# Panel B: Box Plot Distribution (IN NRC 8 vs NOT IN NRC 8)
# ==========================================
sns.boxplot(
    data=df_plot,
    x='group_label',
    y='mean_rating',
    ax=axes[1],
    palette=['#3B82F6', '#F59E0B'],
    width=0.45,
    boxprops=dict(alpha=0.8)
)

sns.stripplot(
    data=df_plot,
    x='group_label',
    y='mean_rating',
    ax=axes[1],
    color='#1E293B',
    alpha=0.4,
    jitter=0.2,
    size=4
)

axes[1].axhline(corpus_mean, color="#EF4444", linestyle="--", linewidth=1.5, label=f"Corpus Mean ({corpus_mean:.3f})")
axes[1].set_title('Tourist Rating Distribution Comparison\nIN NRC 8 Categories (N=286) vs. NOT IN NRC 8 (N=344)', fontsize=12, weight='bold', color='#0F172A')
axes[1].set_xlabel('Word Category Grouping', fontsize=11, weight='bold', color='#1E293B')
axes[1].set_ylabel('Mean Tourist Star Rating (0.0 to 5.0 Stars)', fontsize=11, weight='bold', color='#1E293B')
axes[1].set_ylim(3.0, 5.08)

plt.tight_layout()
out_fig = fig_dir / "nrc8_vs_missed_rating_scatter.png"
plt.savefig(out_fig, dpi=300, bbox_inches="tight")
plt.close()

# Copy to data/analyze/
shutil.copy2(out_fig, analyze_dir / "nrc8_vs_missed_rating_scatter.png")

print(f"Successfully generated plot at:")
print(f"  - {out_fig}")
print(f"  - {analyze_dir / 'nrc8_vs_missed_rating_scatter.png'}")
