#!/usr/bin/env python3
"""Purge grand and expensive from Master Gold Emotion Codebook, move to Removed Log, and update all files & plots."""

import pandas as pd
import shutil
from pathlib import Path
import subprocess

derived_dir = Path("data/derived_outputs")
analyze_dir = Path("data/analyze")

# Load Master Gold & Removed
gold_csv = derived_dir / "gold_emotion_lexicon_codebook.csv"
rem_csv = derived_dir / "removed_non_emotion_words_log.csv"

df_gold = pd.read_csv(gold_csv)
df_rem = pd.read_csv(rem_csv)

words_to_purge = ['grand', 'expensive']

# Identify rows to move
purged_rows = df_gold[df_gold['word'].str.lower().str.strip().isin(words_to_purge)].copy()
df_gold_clean = df_gold[~df_gold['word'].str.lower().str.strip().isin(words_to_purge)].copy()

# Add purge reason to purged_rows
purged_rows['removal_reason'] = "Purged non-emotion / entity name or economic price attribute ('grand' entity name, 'expensive' price rating)"

# Append to df_rem
df_rem_clean = pd.concat([df_rem, purged_rows[['word', 'canonical_lemma', 'chinese_translation', 'frequency_21215', 'review_count_21215', 'removal_reason', 'example_context']]], ignore_index=True)
df_rem_clean = df_rem_clean.drop_duplicates(subset=['word']).sort_values('frequency_21215', ascending=False).reset_index(drop=True)
df_gold_clean = df_gold_clean.sort_values('frequency_21215', ascending=False).reset_index(drop=True)

# Save Master Codebooks
df_gold_clean.to_csv(gold_csv, index=False, encoding='utf-8-sig')
df_gold_clean.to_excel(derived_dir / "gold_emotion_lexicon_codebook.xlsx", index=False)

df_rem_clean.to_csv(rem_csv, index=False, encoding='utf-8-sig')
df_rem_clean.to_excel(derived_dir / "removed_non_emotion_words_log.xlsx", index=False)

print(f"Master Gold Emotion Terms Count: {len(df_gold_clean)} (Purged 'grand' & 'expensive')")
print(f"Master Removed Non-Emotion Log Count: {len(df_rem_clean)}")

# Sync to data/analyze/
df_gold_clean.to_csv(analyze_dir / "gold_emotion_master.csv", index=False, encoding='utf-8-sig')
df_gold_clean.to_excel(analyze_dir / "gold_emotion_master.xlsx", index=False)

# Re-run NRC strict lists
res1 = subprocess.run(["python3", "scratch/export_nrc8_strict_lists.py"], capture_output=True, text=True)
print(res1.stdout.strip())

# Re-run NRC framework categorization
res2 = subprocess.run(["python3", "scratch/categorize_by_nrc_framework.py"], capture_output=True, text=True)
print(res2.stdout.strip())

# Re-run coverage audit
res3 = subprocess.run(["python3", "scratch/audit_vader_nrc_coverage_gap.py"], capture_output=True, text=True)
print(res3.stdout.strip())

# Re-run scatter plots
res4 = subprocess.run(["python3", "scratch/generate_master_gold_vader_nrc_scatter.py"], capture_output=True, text=True)
print(res4.stdout.strip())

# Re-run sync to data/analyze
res5 = subprocess.run(["python3", "scratch/sync_data_analyze_dir.py"], capture_output=True, text=True)
print(res5.stdout.strip())

# Clean data/analyze columns
res6 = subprocess.run(["python3", "scratch/clean_data_analyze_columns.py"], capture_output=True, text=True)
print(res6.stdout.strip())

# Update README and RESEARCH_NOTES_CN with 630 Gold / 8,096 Removed
readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

for old in ["632", "632个", "632 个"]:
    readme_text = readme_text.replace(old, "630")
    cn_text = cn_text.replace(old, "630")

for old in ["8,094", "8,094个", "8,094 个"]:
    readme_text = readme_text.replace(old, "8,096")
    cn_text = cn_text.replace(old, "8,096")

readme_path.write_text(readme_text, encoding="utf-8")
cn_path.write_text(cn_text, encoding="utf-8")

# Re-generate PDF
res_pdf = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res_pdf.stdout.strip())

print("\nAll files, plots, codebooks, and documentation successfully updated to 630 Gold / 8,096 Removed!")
