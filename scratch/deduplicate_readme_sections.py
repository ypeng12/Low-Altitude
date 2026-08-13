#!/usr/bin/env python3
"""Deduplicate NRC section from README.md, RESEARCH_NOTES_CN.md, and RESEARCH_NOTES.md."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")
en_path = Path("RESEARCH_NOTES.md")

for path in [readme_path, cn_path, en_path]:
    if path.exists():
        text = path.read_text(encoding="utf-8")
        
        # Check if "### 📊 7. NRC Lexicon Mapping" or similar duplicate exists
        dup_start = text.find("### 📊 7. NRC Lexicon Mapping")
        if dup_start == -1:
            dup_start = text.find("### 📊 7. NRC 词典映射")
        if dup_start == -1:
            dup_start = text.find("## 📊 7. NRC Lexicon Mapping")
            
        if dup_start != -1:
            # Cut off the duplicate section
            text = text[:dup_start].strip() + "\n"
            path.write_text(text, encoding="utf-8")
            print(f"Successfully removed duplicate NRC section from '{path.name}'!")
