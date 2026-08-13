#!/usr/bin/env python3
"""Copy master gold emotion codebook to data/cleaned_datasets/gold_emotion_lexicon_master.xlsx."""

import shutil
from pathlib import Path

src_xlsx = Path("data/derived_outputs/gold_emotion_lexicon_codebook.xlsx")
src_csv = Path("data/derived_outputs/gold_emotion_lexicon_codebook.csv")

dst_dir = Path("data/cleaned_datasets")
dst_dir.mkdir(parents=True, exist_ok=True)

dst_xlsx = dst_dir / "gold_emotion_lexicon_master.xlsx"
dst_csv = dst_dir / "gold_emotion_lexicon_master.csv"

shutil.copy2(src_xlsx, dst_xlsx)
shutil.copy2(src_csv, dst_csv)

print(f"Successfully copied Master Gold Emotion Lexicon to:")
print(f"  - XLSX: {dst_xlsx}")
print(f"  - CSV:  {dst_csv}")
