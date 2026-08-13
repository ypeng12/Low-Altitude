#!/usr/bin/env python3
"""Calculate exact word count % vs review frequency % for Cause 2."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

c2_words = {"great", "awesome", "fantastic", "incredible", "incredibly", "nice", "fabulous", "phenomenal", "unbeatable", "primo"}

missed = []
for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    if len(tags) == 0:
        missed.append(row)

df_missed = pd.DataFrame(missed)

total_missed_words = len(df_missed)
total_missed_freq = df_missed['frequency_21215'].sum()

c2_df = df_missed[df_missed['word'].isin(c2_words) | df_missed['canonical_lemma'].isin(c2_words)]

c2_word_count = len(c2_df)
c2_freq_sum = c2_df['frequency_21215'].sum()

print("=== 🔬 CAUSE 2 DUAL PERCENTAGE AUDIT ===")
print(f"Total Missed Unique Words: {total_missed_words}")
print(f"Total Missed Review Mentions: {total_missed_freq:,}\n")

print(f"Cause 2 Unique Word Count: {c2_word_count} words ({c2_word_count / total_missed_words * 100:.2f}% of unique words)")
print(f"Cause 2 Review Frequency Sum: {c2_freq_sum:,} mentions ({c2_freq_sum / total_missed_freq * 100:.2f}% of total missed review frequency)")
