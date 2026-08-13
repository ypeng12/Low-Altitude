#!/usr/bin/env python3
"""Script to add explicit mathematical addition breakdown for Gold Emotion Lexicon into README.md."""

from pathlib import Path

readme_path = Path("README.md")

lines = readme_path.read_text(encoding="utf-8").splitlines()

addition_box = """
> [!IMPORTANT]
> **Gold Emotion Lexicon Composition & Addition Formula Across Stages**:
> 1. **Initial 2,500-Review Sample Gold Lexicon ($N=2,500$)**:
>    $$\\text{Stage 1 Discovery (500 Reviews: 372 Words)} + \\text{Stage 2 Expansion (2,000 Reviews: 173 Words)} = \\mathbf{545 \\text{ Gold Words}}$$
> 2. **Master Full-Corpus Gold Lexicon ($N=21,215$)**:
>    $$\\text{Initial 2,500 Sample Gold Lexicon (545 Words)} + \\text{Stage Final New Words (18,901 Reviews: 63 Words)} = \\mathbf{608 \\text{ Master Gold Words}}$$
"""

new_lines = []
inserted = False
for l in lines:
    new_lines.append(l)
    if "### 1. Step-by-Step Evolution & Methodology" in l and not inserted:
        new_lines.append(addition_box)
        inserted = True

if inserted:
    readme_path.write_text("\n".join(new_lines), encoding="utf-8")
    print("Successfully updated README.md with explicit Gold Emotion addition formula!")
else:
    print("Warning: Section header not found.")
