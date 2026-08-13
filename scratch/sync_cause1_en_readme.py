#!/usr/bin/env python3
"""Replace Cause 1 in README.md cleanly using exact substring search."""

from pathlib import Path

readme_path = Path("README.md")
readme_text = readme_path.read_text(encoding="utf-8")

cause1_en_formal = """1. **Morphological & Participle Derivation Gaps (Pure Morphological Variants)**:
   - **Participle Forms (-ing / -ed)**: e.g., *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), reassuring (97)*.
   - **Adverbs & Superlatives (-ly, -est, -er)**: e.g., *better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132), smoothest (105), luckily (96)*.
   - **Empirical Validation**: Among the 127 pure morphological variant words, **48.82% (62 words) have base dictionary roots (e.g., *amaze, love, impress, inspire, scare, thrill, good, safe*) already present in NRC**. However, static string matching fails to capture them, omitting **88.7% (15,581 review mentions)** of high-frequency emotional expressions.
   - *Finding*: Generic NRC lexicons lack morphological derivation rules, causing significant classification omissions."""

start_r = readme_text.find("1. **Morphological & Participle")
end_r = readme_text.find("2. **Omission of")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + cause1_en_formal + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Cleanly updated README.md!")
else:
    print(f"Warning: start_r={start_r}, end_r={end_r}")
