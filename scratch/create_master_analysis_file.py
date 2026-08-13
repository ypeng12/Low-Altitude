#!/usr/bin/env python3
"""Create a dedicated working copy of gold_emotion_lexicon_codebook.xlsx for next-step analysis."""

import shutil
from pathlib import Path

root_dir = Path("data/derived_outputs")

src_xlsx = root_dir / "gold_emotion_lexicon_codebook.xlsx"
src_csv = root_dir / "gold_emotion_lexicon_codebook.csv"

dst_xlsx = root_dir / "gold_emotion_lexicon_codebook_analysis.xlsx"
dst_csv = root_dir / "gold_emotion_lexicon_codebook_analysis.csv"

shutil.copy2(src_xlsx, dst_xlsx)
shutil.copy2(src_csv, dst_csv)

print(f"Successfully copied Master Gold Emotion Lexicon Codebook to:")
print(f"  - XLSX: {dst_xlsx}")
print(f"  - CSV:  {dst_csv}")
