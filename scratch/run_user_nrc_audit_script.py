#!/usr/bin/env python3
"""Run the exact script provided by the user on gold_emotion_master.csv (630 words)."""

import pandas as pd
from pathlib import Path
import json

# Load Master Gold Emotion Codebook (630 words)
my_file = Path("data/analyze/gold_emotion_master.csv")
df = pd.read_csv(my_file)

# 统一成小写，去掉前后空格
df["word_clean"] = (
    df["word"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# 去重
words = df["word_clean"].dropna().drop_duplicates()

print("你的词数:", len(words))

# Load official nrc_en.json and build full table
pkg_file = Path('/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/nrclex/data/nrc_en.json')
data = json.loads(pkg_file.read_text(encoding='utf-8'))

rows = []
for w, tags in data.items():
    row = {"word": w, "anger": 0, "anticipation": 0, "disgust": 0, "fear": 0, "joy": 0, "sadness": 0, "surprise": 0, "trust": 0, "positive": 0, "negative": 0}
    for t in tags:
        if t in row:
            row[t] = 1
    rows.append(row)
nrc = pd.DataFrame(rows)

emotion_cols = [
    "anger",
    "anticipation",
    "disgust",
    "fear",
    "joy",
    "sadness",
    "surprise",
    "trust"
]

polarity_cols = [
    "positive",
    "negative"
]

all_affect_cols = emotion_cols + polarity_cols

result = pd.DataFrame({
    "word": words
})

result = result.merge(
    nrc,
    on="word",
    how="left",
    indicator=True
)

result["in_nrc_vocabulary"] = result["_merge"].eq("both")

for col in all_affect_cols:
    result[col] = result[col].fillna(0).astype(int)

result["has_8_emotion"] = (
    result[emotion_cols].sum(axis=1) > 0
)

result["has_polarity"] = (
    result[polarity_cols].sum(axis=1) > 0
)

mask_emotion = (
    result["in_nrc_vocabulary"]
    & result["has_8_emotion"]
)

mask_polarity_only = (
    result["in_nrc_vocabulary"]
    & ~result["has_8_emotion"]
    & result["has_polarity"]
)

mask_all_zero = (
    result["in_nrc_vocabulary"]
    & ~result["has_8_emotion"]
    & ~result["has_polarity"]
)

mask_not_nrc = (
    ~result["in_nrc_vocabulary"]
)

total = len(result)

n_in_vocab = result["in_nrc_vocabulary"].sum()

n_emotion = mask_emotion.sum()
n_polarity_only = mask_polarity_only.sum()
n_all_zero = mask_all_zero.sum()
n_not_nrc = mask_not_nrc.sum()

print("\n================ NRC COVERAGE ================\n")

print(
    f"在 NRC vocabulary 中: "
    f"{n_in_vocab} / {total} "
    f"({n_in_vocab / total:.2%})"
)

print(
    f"8-emotion 至少一个: "
    f"{n_emotion} / {total} "
    f"({n_emotion / total:.2%})"
)

print(
    f"只有 Positive / Negative: "
    f"{n_polarity_only} / {total} "
    f"({n_polarity_only / total:.2%})"
)

print(
    f"在 NRC 中但 10 标签全 0: "
    f"{n_all_zero} / {total} "
    f"({n_all_zero / total:.2%})"
)

print(
    f"完全不在 NRC: "
    f"{n_not_nrc} / {total} "
    f"({n_not_nrc / total:.2%})"
)

assert (
    n_emotion
    + n_polarity_only
    + n_all_zero
    + n_not_nrc
    == total
)

assert (
    n_emotion
    + n_polarity_only
    + n_all_zero
    == n_in_vocab
)

print("\n检查通过 ✅")
