#!/usr/bin/env python3
"""Generate iconic VADER Score vs. Tourist Star Rating Scatter Plot for Master Gold Emotion Words (Rating 0 to 5)."""

import shutil
from pathlib import Path
import re
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nrclex import NRCLex

fig_dir = Path("figures/nrc_emotion_plots")
fig_dir.mkdir(parents=True, exist_ok=True)
analyze_dir = Path("data/analyze")

# Load Master files & full corpus
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
df_eng = pd.read_csv("data/cleaned_datasets/tripadvisor_level3_english_v2.csv")

# VADER & NRC Lexicons
vader_lex = SentimentIntensityAnalyzer().lexicon
nrc_lex = NRCLex().__lexicon__

NRC8 = ("joy", "trust", "fear", "surprise", "anticipation", "sadness", "anger", "disgust")
PRIMARY_ORDER = ("joy", "fear", "trust", "surprise", "anticipation", "sadness", "anger", "disgust")

COLORS = {
    "JOY": "#16A34A",          # Green
    "FEAR": "#DC2626",         # Red
    "TRUST": "#1D4ED8",        # Blue
    "SURPRISE": "#9333EA",      # Purple
    "ANTICIPATION": "#EA580C", # Orange
    "SADNESS": "#64748B",      # Slate Gray
    "ANGER": "#B91C1C",        # Dark Red
    "DISGUST": "#92400E",      # Brown
    "DOMAIN_AWE": "#F59E0B"    # Gold / Yellow for Domain-Specific Awe Misses
}

# Calculate mean review rating and review count for each word in Gold Lexicon
gold_words_set = set(df_gold['word'].str.lower().str.strip())
word_ratings = defaultdict(list)
word_counts = defaultdict(int)

print("Calculating word-level mean ratings across N=21,215 reviews...")
for row in df_eng.itertuples():
    text = f"{row.review_title if pd.notna(row.review_title) else ''} {row.review_text if pd.notna(row.review_text) else ''}".lower()
    tokens = set(re.findall(r"\b[a-zA-Z]{2,}\b", text))
    r_rating = float(row.rating)
    for w in tokens:
        if w in gold_words_set:
            word_ratings[w].append(r_rating)
            word_counts[w] += 1

# Prepare scatter data
scatter_records = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    ratings = word_ratings[w]
    if not ratings:
        ratings = [5.0]  # default fallback
        
    mean_rat = float(np.mean(ratings))
    rev_cnt = len(ratings)
    vader_score = float(vader_lex.get(w, vader_lex.get(lemma, 0.0)))
    
    # Assign display category
    nrc_emotions = set(nrc_lex.get(w, nrc_lex.get(lemma, []))) & set(NRC8)
    display_cat = "DOMAIN_AWE"
    if nrc_emotions:
        for p in PRIMARY_ORDER:
            if p in nrc_emotions:
                display_cat = p.upper()
                break

    scatter_records.append({
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': row.chinese_translation,
        'vader_score': vader_score,
        'mean_rating': mean_rat,
        'review_count': rev_cnt,
        'display_category': display_cat
    })

df_scatter = pd.DataFrame(scatter_records).sort_values('review_count', ascending=False).reset_index(drop=True)

# Plotting
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(16, 10), dpi=300)

legend_order = ["JOY", "FEAR", "TRUST", "SURPRISE", "ANTICIPATION", "SADNESS", "ANGER", "DISGUST", "DOMAIN_AWE"]
legend_labels = {
    "JOY": "Joy", "FEAR": "Fear / Risk Anxiety", "TRUST": "Trust / Security",
    "SURPRISE": "Surprise", "ANTICIPATION": "Anticipation", "SADNESS": "Sadness / Regret",
    "ANGER": "Anger / Annoyance", "DISGUST": "Disgust / Discomfort",
    "DOMAIN_AWE": "Domain-Specific Awe / High-Arousal Appraisal (NRC Misses)"
}

for cat in legend_order:
    group = df_scatter[df_scatter['display_category'] == cat]
    if group.empty:
        continue
        
    # Bubble size proportional to review count
    sizes = 45 + 35 * np.log10(np.maximum(group['review_count'], 1))
    
    ax.scatter(
        group['vader_score'],
        group['mean_rating'],
        s=sizes,
        color=COLORS[cat],
        edgecolor="#1E293B",
        linewidth=0.8,
        alpha=0.85 if cat == "DOMAIN_AWE" else 0.75,
        label=f"{legend_labels[cat]} (words={len(group)})"
    )

# Baseline Reference Lines
corpus_mean_rating = float(df_eng['rating'].mean())
ax.axhline(corpus_mean_rating, color="#EF4444", linestyle=":", linewidth=1.8, label=f"Corpus Mean Star Rating ({corpus_mean_rating:.3f})")
ax.axvline(0.0, color="#64748B", linestyle="--", linewidth=1.2)

# Annotate High-Frequency & Notable Words
key_words_to_annotate = [
    'great', 'amazing', 'breathtaking', 'awesome', 'fantastic', 'incredible', 'stunning', 'unforgettable',
    'scared', 'fear', 'nervous', 'terrified', 'anxious', 'jitters', 'claustrophobia', 'reassuring', 'safe',
    'disappointed', 'regret', 'sorry', 'horrible', 'terrible', 'annoying', 'thrilling', 'exhilarating',
    'sublime', 'mesmerizing', 'glad', 'happy', 'love', 'satisfied', 'relaxing', 'calm'
]

try:
    from adjustText import adjust_text
    texts = []
    for row in df_scatter[df_scatter['word'].isin(key_words_to_annotate)].itertuples():
        texts.append(ax.text(row.vader_score, row.mean_rating, row.word, fontsize=9.5, weight='bold', color="#0F172A"))
    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="->", color="#475569", lw=0.6))
except Exception as e:
    print("adjustText not available, using simple text placement:", e)
    for row in df_scatter[df_scatter['word'].isin(key_words_to_annotate)].itertuples():
        ax.annotate(row.word, (row.vader_score, row.mean_rating), xytext=(3, 3), textcoords="offset points", fontsize=8.5, weight="bold")

ax.set_title(
    "Master Gold Emotion Lexicon Scatter Plot: VADER Valence (-4.0 to +4.0) vs. Mean Tourist Star Rating (0.0 to 5.0 Stars)\n"
    "[Color Coded by NRC 8 Emotion Categories & Domain-Specific Awe Misses; Bubble Size = Review Count]",
    fontsize=14, fontweight="bold", pad=15, color="#0F172A"
)
ax.set_xlabel("VADER Lexicon Word Valence Score (-4.0 to +4.0)", fontsize=12, fontweight="bold", color="#1E293B")
ax.set_ylabel("Mean Tourist Star Rating of Reviews Containing the Word (0.0 to 5.0 Stars)", fontsize=12, fontweight="bold", color="#1E293B")

# Set Y-axis strictly 0.0 to 5.2
ax.set_xlim(-4.2, 4.2)
ax.set_ylim(0.0, 5.2)
ax.set_yticks([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])

ax.legend(loc="lower left", fontsize=9.5, framealpha=0.95)

plt.tight_layout()
out_fig = fig_dir / "master_gold_vader_nrc_scatter.png"
plt.savefig(out_fig, dpi=300, bbox_inches="tight")
plt.close()

# Copy to data/analyze/
shutil.copy2(out_fig, analyze_dir / "master_gold_vader_nrc_scatter.png")

print(f"Successfully generated master scatter plot (Rating 0 to 5) at:")
print(f"  - {out_fig}")
print(f"  - {analyze_dir / 'master_gold_vader_nrc_scatter.png'}")
