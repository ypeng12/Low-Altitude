#!/usr/bin/env python3
"""Verify no 17 rescued table remains in documentation files."""

from pathlib import Path

files = [Path("README.md"), Path("RESEARCH_NOTES_CN.md"), Path("RESEARCH_NOTES.md")]

for f in files:
    if f.exists():
        text = f.read_text(encoding="utf-8")
        assert "17 Rescued" not in text, f"17 Rescued table should be deleted from {f.name}"
        assert "breathtaking" in text, f"Class 3 key terms should be in {f.name}"
        print(f"✅ Verified '{f.name}' cleanly!")
