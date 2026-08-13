#!/usr/bin/env python3
"""Synchronize all Master Gold Codebook analysis files directly into data/analyze/ directory."""

import shutil
from pathlib import Path

analyze_dir = Path("data/analyze")
analyze_dir.mkdir(parents=True, exist_ok=True)

src_dir = Path("data/derived_outputs")
cleaned_dir = Path("data/cleaned_datasets")

# Files to copy/sync into data/analyze/
file_mappings = [
    (cleaned_dir / "gold_emotion_lexicon_master.xlsx", analyze_dir / "gold_emotion_master.xlsx"),
    (cleaned_dir / "gold_emotion_lexicon_master.csv", analyze_dir / "gold_emotion_master.csv"),
    (src_dir / "nrc_words_missed.xlsx", analyze_dir / "nrc_words_missed.xlsx"),
    (src_dir / "nrc_words_missed.csv", analyze_dir / "nrc_words_missed.csv"),
    (src_dir / "nrc_words_included.xlsx", analyze_dir / "nrc_words_included.xlsx"),
    (src_dir / "nrc_words_included.csv", analyze_dir / "nrc_words_included.csv"),
    (src_dir / "gold_emotion_categorized_by_nrc.xlsx", analyze_dir / "gold_emotion_categorized_by_nrc.xlsx"),
    (src_dir / "gold_emotion_categorized_by_nrc.csv", analyze_dir / "gold_emotion_categorized_by_nrc.csv")
]

for src, dst in file_mappings:
    if src.exists():
        shutil.copy2(src, dst)
        print(f"Copied {src.name} -> {dst}")
    else:
        print(f"Warning: {src} not found")

print("\nSuccessfully synchronized all NRC analysis files into data/analyze/!")
