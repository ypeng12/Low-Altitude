#!/usr/bin/env python3
"""Remove RESEARCH_NOTES_CN.md link from README.md header."""

from pathlib import Path

readme_path = Path("README.md")
text = readme_path.read_text(encoding="utf-8")

if "RESEARCH_NOTES_CN.md" in text:
    text = text.replace("> - 🇨🇳 **Chinese Lab Notes**: `RESEARCH_NOTES_CN.md`\n", "")
    text = text.replace("> - 🇨🇳 **Chinese Lab Notes**: `RESEARCH_NOTES_CN.md`", "")
    readme_path.write_text(text, encoding="utf-8")
    print("Successfully removed RESEARCH_NOTES_CN.md link from README.md!")
