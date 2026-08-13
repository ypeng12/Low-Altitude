#!/usr/bin/env python3
"""Remove any silly '⭐ (Recommended)' tag from documentation files."""

from pathlib import Path

files = [Path("README.md"), Path("RESEARCH_NOTES_CN.md"), Path("RESEARCH_NOTES.md")]

for f in files:
    if f.exists():
        text = f.read_text(encoding="utf-8")
        if "⭐ (Recommended)" in text or "⭐ 【推荐使用！】" in text or "⭐ (推荐)" in text:
            text = text.replace("⭐ (Recommended)", "")
            text = text.replace("⭐ 【推荐使用！】", "")
            text = text.replace("⭐ (推荐)", "")
            f.write_text(text, encoding="utf-8")
            print(f"Successfully cleaned '{f.name}'!")
