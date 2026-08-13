#!/usr/bin/env python3
"""Check for any remaining Recommended or ⭐ tags in README.md."""

from pathlib import Path

readme_path = Path("README.md")
text = readme_path.read_text(encoding="utf-8")

found = []
for idx, line in enumerate(text.splitlines(), 1):
    if "Recommended" in line or "recommended" in line or "⭐" in line:
        found.append((idx, line))

print("=== SEARCH RESULTS IN README.MD ===")
for line_num, line in found:
    print(f"Line {line_num:3d}: {line}")
