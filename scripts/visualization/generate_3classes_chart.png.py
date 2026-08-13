#!/usr/bin/env python3
"""Generate publication-ready academic chart for the 3 Core Classes of NRC Lexicon Misses."""

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 11

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [1, 1.2]})

# Chart 1: Donut Chart by Unique Word Count (N=272)
labels = [
    'Class 1: Morphological Derivation Gaps\n(127 words, 46.7%)',
    'Class 2: Web 2.0 Colloquial Superlatives\n(128 words, 47.1%)',
    'Class 3: Low-Altitude Domain Lexicon\n(17 words, 6.3%)'
]
sizes = [127, 128, 17]
colors = ['#3498db', '#e74c3c', '#2ecc71']
explode = (0.02, 0.02, 0.05)

wedges, texts, autotexts = ax1.pie(
    sizes, explode=explode, labels=labels, colors=colors,
    autopct='%1.1f%%', startangle=140, pctdistance=0.75,
    textprops=dict(color="black", fontsize=10, weight="bold")
)

# Draw circle for donut
centre_circle = plt.Circle((0, 0), 0.55, fc='white')
ax1.add_artist(centre_circle)
ax1.set_title('A. Breakdown by Unique Word Count (N = 272)', fontsize=13, weight='bold', pad=15)

# Chart 2: Horizontal Bar Chart by Review Mention Frequency
categories = [
    'Class 2: Web 2.0 Colloquial Superlatives\n(great, awesome, fantastic, nice...)',
    'Class 1: Morphological Derivation Gaps\n(-ing, -ed, -ly, -est, -er variants)',
    'Class 3: Low-Altitude Domain Lexicon\n(Aerial Awe & Somatic Flight Risk)'
]
freq_mentions = [28401, 17565, 2862]
bar_colors = ['#e74c3c', '#3498db', '#2ecc71']

bars = ax2.barh(categories, freq_mentions, color=bar_colors, height=0.55, edgecolor='black', linewidth=1)
ax2.set_xlabel('Total Review Mention Frequency (N = 48,828)', fontsize=11, weight='bold')
ax2.set_title('B. Breakdown by Total Corpus Mention Frequency', fontsize=13, weight='bold', pad=15)
ax2.invert_yaxis()  # top-down

# Add data labels
for bar in bars:
    width = bar.get_width()
    pct = (width / 48828) * 100
    ax2.text(width + 800, bar.get_y() + bar.get_height()/2, f'{width:,} ({pct:.1f}%)',
             va='center', ha='left', fontsize=10, weight='bold', color='#2c3e50')

ax2.set_xlim(0, 35000)

plt.suptitle('Empirical Audit of NRC Lexicon Coverage Gaps: Word Count vs. Mention Frequency', fontsize=15, weight='bold', y=1.02)
plt.tight_layout()

output_dir = Path("figures/nrc_emotion_plots")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "nrc_missed_3classes_chart.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Successfully generated publication-ready chart at: {output_path}")
