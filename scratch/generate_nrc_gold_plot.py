#!/usr/bin/env python3
"""Generate publication-ready plot for Master Gold Emotion Lexicon NRC Mapping."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

root_dir = Path("data/derived_outputs")
fig_dir = Path("figures/nrc_emotion_plots")
fig_dir.mkdir(parents=True, exist_ok=True)

df_mapped = pd.read_csv(root_dir / "gold_emotion_nrc_mapped.csv")

# Set seaborn style
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [1, 1.4]})

# 1. Donut Chart: NRC Lexicon Coverage vs Domain-Specific Misses
nrc_coverage_data = [358, 274]
labels = ['NRC Covered (56.7%)', 'Domain-Specific Gaps (43.3%)']
colors_donut = ['#3B82F6', '#EF4444']

axes[0].pie(
    nrc_coverage_data,
    labels=labels,
    colors=colors_donut,
    autopct='%1.1f%%',
    startangle=140,
    pctdistance=0.75,
    textprops={'fontsize': 11, 'weight': 'bold'},
    wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
)
axes[0].set_title('Master Gold Lexicon (N=632)\nNRC Lexicon Coverage Breakdown', fontsize=13, weight='bold', color='#1E293B', pad=15)

# 2. Bar Chart: NRC 8 Basic Emotions Count in Gold Lexicon
nrc_8_counts = {
    'Joy': 119,
    'Trust': 93,
    'Anticipation': 79,
    'Fear': 75,
    'Sadness': 72,
    'Surprise': 69,
    'Anger': 53,
    'Disgust': 46
}

cats = list(nrc_8_counts.keys())
counts = list(nrc_8_counts.values())
bar_colors = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#64748B', '#EC4899', '#EF4444', '#D97706']

bars = axes[1].barh(cats, counts, color=bar_colors, edgecolor='none', height=0.65)
axes[1].invert_yaxis()  # top-down

# Add count labels
for bar in bars:
    w = bar.get_width()
    axes[1].text(w + 2, bar.get_y() + bar.get_height()/2, f'{int(w)} words ({w/632*100:.1f}%)', va='center', ha='left', fontsize=10, weight='bold', color='#334155')

axes[1].set_title('NRC 8 Basic Emotion Categories\nDistribution across Master Gold Lexicon', fontsize=13, weight='bold', color='#1E293B', pad=15)
axes[1].set_xlabel('Number of Emotion Words', fontsize=11, weight='bold', color='#475569')
axes[1].set_xlim(0, 145)

plt.tight_layout()
out_fig = fig_dir / "nrc_mapping_gold_lexicon_distribution.png"
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
print(f"Successfully generated plot at: {out_fig}")
