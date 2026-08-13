#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md with exact Master Gold Codebook counts (637) and Removed Log counts (8089)."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

# Replace counts in README
readme_text = readme_text.replace("628 Master Gold", "637 Master Gold")
readme_text = readme_text.replace("628 Words", "637 Words")
readme_text = readme_text.replace("608 Master Gold", "637 Master Gold")
readme_text = readme_text.replace("608 Words", "637 Words")
readme_text = readme_text.replace("8,098", "8,089")

# Replace counts in CN
cn_text = cn_text.replace("628 个 Master 金标准", "637 个 Master 金标准")
cn_text = cn_text.replace("628 个词", "637 个词")
cn_text = cn_text.replace("608 个词", "637 个词")
cn_text = cn_text.replace("8,098", "8,089")

readme_path.write_text(readme_text, encoding="utf-8")
cn_path.write_text(cn_text, encoding="utf-8")

print("Successfully updated README.md and RESEARCH_NOTES_CN.md with 637 Gold Lexicon counts!")
