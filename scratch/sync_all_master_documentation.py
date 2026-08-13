#!/usr/bin/env python3
"""Synchronize exact master counts (632 Gold / 8094 Removed) across README.md, RESEARCH_NOTES_CN.md, and Chinese PDF."""

from pathlib import Path
import subprocess

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

# Comprehensive replacements for README.md
for old_gold in ["648 Master Gold", "648 Words", "637 Master Gold", "637 Words", "628 Master Gold", "628 Words", "608 Master Gold", "608 Words", "545 Gold"]:
    readme_text = readme_text.replace(old_gold, "632 Master Gold" if "Master" in old_gold else "632 Words")

for old_rem in ["8,078", "8,089", "8,098", "8,118"]:
    readme_text = readme_text.replace(old_rem, "8,094")

# Comprehensive replacements for RESEARCH_NOTES_CN.md
for old_cn_gold in ["648 个 Master 金标准", "648 个词", "637 个 Master 金标准", "637 个词", "628 个 Master 金标准", "628 个词", "608 个词"]:
    cn_text = cn_text.replace(old_cn_gold, "632 个 Master 金标准" if "Master" in old_cn_gold else "632 个词")

for old_cn_rem in ["8,078", "8,089", "8,098", "8,118"]:
    cn_text = cn_text.replace(old_cn_rem, "8,094")

readme_path.write_text(readme_text, encoding="utf-8")
cn_path.write_text(cn_text, encoding="utf-8")

print("Successfully updated README.md and RESEARCH_NOTES_CN.md!")

# Re-generate Chinese PDF report
res = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res.stdout.strip())
