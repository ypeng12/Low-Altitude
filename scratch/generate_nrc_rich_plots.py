#!/usr/bin/env python3
"""Generate rich publication-ready graphs and table visuals for NRC mapping & Gold Lexicon."""

import shutil
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

fig_dir = Path("figures/nrc_emotion_plots")
fig_dir.mkdir(parents=True, exist_ok=True)
analyze_dir = Path("data/analyze")

# Load Master files
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
df_misses = pd.read_csv("data/analyze/nrc_words_missed.csv")
df_hits = pd.read_csv("data/analyze/nrc_words_included.csv")
df_nrc_cat = pd.read_csv("data/analyze/gold_emotion_categorized_by_nrc.csv")

# Set theme
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# Graph 1: NRC 8 Emotions vs NRC Misses Comparison with Word Annotations
# ==========================================
fig, axes = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={'width_ratios': [1.1, 1]})

# Left Panel: Top Missed Words Frequency Bar Chart
top_misses = df_misses.head(15)
bars1 = axes[0].barh(top_misses['word'], top_misses['frequency_21215'], color='#EF4444', edgecolor='none', height=0.65)
axes[0].invert_yaxis()
axes[0].set_title('Top 15 Domain-Specific Emotion Words MISSED by NRC\n(Massive Coverage Gaps in Generic Lexicons)', fontsize=13, weight='bold', color='#1E293B', pad=15)
axes[0].set_xlabel('Total Term Frequency across N=21,215 Reviews', fontsize=11, weight='bold', color='#475569')

for bar in bars1:
    w = bar.get_width()
    axes[0].text(w + 100, bar.get_y() + bar.get_height()/2, f'{int(w):,} times', va='center', ha='left', fontsize=9, weight='bold', color='#B91C1C')

# Right Panel: NRC 8 Categories with Representative Words Annotations
nrc_cat_summary = [
    ('NRC_JOY', 119, 'beautiful, friendly, wonderful, fun, glad, happy, love'),
    ('NRC_FEAR', 66, 'nervous, afraid, fear, worry, terrified, anxious, panic'),
    ('NRC_TRUST', 33, 'expert, assured, stable, genuine, reliable, reassuring'),
    ('NRC_SADNESS', 42, 'disappointed, regret, sick, sorry, upset, dismay'),
    ('NRC_SURPRISE', 12, 'spectacular, unique, surprised, marvel, sudden'),
    ('NRC_ANGER', 9, 'noisy, annoying, frustration, ridiculous, irritating'),
    ('NRC_ANTICIPATION', 3, 'ready, hungry, uneasiness'),
    ('NRC_DISGUST', 2, 'spoil, weird')
]

df_nrc_sum = pd.DataFrame(nrc_cat_summary, columns=['cat', 'count', 'words'])
df_nrc_sum['label'] = df_nrc_sum['cat'].str.replace('NRC_', '')

bars2 = axes[1].barh(df_nrc_sum['label'], df_nrc_sum['count'], color='#3B82F6', edgecolor='none', height=0.65)
axes[1].invert_yaxis()
axes[1].set_title('NRC 8 Basic Emotion Categories in Gold Lexicon\n(With Sample Words Annotations)', fontsize=13, weight='bold', color='#1E293B', pad=15)
axes[1].set_xlabel('Number of Gold Emotion Words', fontsize=11, weight='bold', color='#475569')

for bar, (idx, row) in zip(bars2, df_nrc_sum.iterrows()):
    w = bar.get_width()
    axes[1].text(w + 2, bar.get_y() + bar.get_height()/2, f'{row["count"]} words: {row["words"][:35]}...', va='center', ha='left', fontsize=8.5, weight='bold', color='#1E40AF')

axes[1].set_xlim(0, 160)
plt.tight_layout()
fig1_path = fig_dir / "nrc_vs_gold_lexicon_comparison.png"
plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# Graph 2: Word Frequency & Emotion Category Bubble / Scatter Chart
# ==========================================
fig, ax = plt.subplots(figsize=(15, 8))

# Select top 50 high-frequency words from df_nrc_cat for clear scatter rendering
df_top50 = df_nrc_cat.sort_values('frequency_21215', ascending=False).head(55).copy()
df_top50['log_freq'] = np.log10(df_top50['frequency_21215'])

# Map categories to numeric y-axis
unique_cats = df_top50['nrc_primary_category'].unique()
cat_to_y = {c: i for i, c in enumerate(unique_cats)}
df_top50['y_pos'] = df_top50['nrc_primary_category'].map(cat_to_y)

# Jitter y positions slightly for readability
np.random.seed(42)
df_top50['y_jitter'] = df_top50['y_pos'] + np.random.uniform(-0.15, 0.15, size=len(df_top50))

scatter = ax.scatter(
    df_top50['frequency_21215'],
    df_top50['y_jitter'],
    s=df_top50['frequency_21215'] ** 0.5 * 12,
    c=df_top50['y_pos'],
    cmap='tab10',
    alpha=0.7,
    edgecolors='white',
    linewidth=1.5
)

# Annotate word text on top of points
for row in df_top50.itertuples():
    ax.annotate(
        row.word,
        (row.frequency_21215, row.y_jitter),
        xytext=(0, 5),
        textcoords='offset points',
        ha='center',
        fontsize=9,
        weight='bold',
        color='#0F172A'
    )

ax.set_xscale('log')
ax.set_yticks(range(len(unique_cats)))
ax.set_yticklabels([c.replace('NRC_', '').replace('(Low-Altitude Domain-Specific Awe / Appraisal)', '(Awe/Domain Misses)') for c in unique_cats], fontsize=10, weight='bold')
ax.set_xlabel('Term Frequency in N=21,215 Reviews (Log Scale)', fontsize=12, weight='bold', color='#1E293B')
ax.set_title('Top 55 Master Gold Emotion Words: Frequency & NRC Category Scatter Map', fontsize=14, weight='bold', color='#0F172A', pad=15)

plt.tight_layout()
fig2_path = fig_dir / "nrc_words_by_category_scatter.png"
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
plt.close()

# Copy figures into data/analyze for easy user viewing
shutil.copy2(fig1_path, analyze_dir / "nrc_vs_gold_lexicon_comparison.png")
shutil.copy2(fig2_path, analyze_dir / "nrc_words_by_category_scatter.png")

print(f"Successfully generated graphs:")
print(f"  - {fig1_path}")
print(f"  - {fig2_path}")
