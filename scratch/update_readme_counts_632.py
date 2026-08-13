#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md with exact Master Gold Codebook counts (632) and Removed Log counts (8094)."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

# Replace counts in README
readme_text = readme_text.replace("648 Master Gold", "632 Master Gold")
readme_text = readme_text.replace("648 Words", "632 Words")
readme_text = readme_text.replace("637 Master Gold", "632 Master Gold")
readme_text = readme_text.replace("637 Words", "632 Words")
readme_text = readme_text.replace("628 Master Gold", "632 Master Gold")
readme_text = readme_text.replace("628 Words", "632 Words")
readme_text = readme_text.replace("608 Master Gold", "632 Master Gold")
readme_text = readme_text.replace("608 Words", "632 Words")
readme_text = readme_text.replace("8,078", "8,094")
readme_text = readme_text.replace("8,089", "8,094")
readme_text = readme_text.replace("8,098", "8,094")

# Replace counts in CN
cn_text = cn_text.replace("648 个 Master 金标准", "632 个 Master 金标准")
cn_text = cn_text.replace("648 个词", "632 个词")
cn_text = cn_text.replace("637 个 Master 金标准", "632 个 Master 金标准")
cn_text = cn_text.replace("637 个词", "632 个词")
cn_text = cn_text.replace("628 个 Master 金标准", "632 个 Master 金标准")
cn_text = cn_text.replace("628 个词", "632 个词")
cn_text = cn_text.replace("608 个词", "632 个词")
cn_text = cn_text.replace("8,078", "8,094")
cn_text = cn_text.replace("8,089", "8,094")
cn_text = cn_text.replace("8,098", "8,094")

readme_path.write_text(readme_text, encoding="utf-8")
cn_path.write_text(cn_text, encoding="utf-8")

print("Successfully updated README.md and RESEARCH_NOTES_CN.md with 632 Gold Lexicon counts!")
