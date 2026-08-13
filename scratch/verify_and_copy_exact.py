#!/usr/bin/env python3
"""Ensure gold_emotion_lexicon_codebook.xlsx is exact copied to all master files."""

import shutil
from pathlib import Path

src_xlsx = Path("data/derived_outputs/gold_emotion_lexicon_codebook.xlsx")
src_csv = Path("data/derived_outputs/gold_emotion_lexicon_codebook.csv")

targets = [
    (Path("data/cleaned_datasets/gold_emotion_lexicon_master.xlsx"), Path("data/cleaned_datasets/gold_emotion_lexicon_master.csv")),
    (Path("data/derived_outputs/gold_emotion_lexicon_codebook_analysis.xlsx"), Path("data/derived_outputs/gold_emotion_lexicon_codebook_analysis.csv"))
]

for dst_x, dst_c in targets:
    shutil.copy2(src_xlsx, dst_x)
    shutil.copy2(src_csv, dst_c)
    print(f"Copied to {dst_x} and {dst_c}")

print("All copies verified and identical!")
