#!/usr/bin/env python3
"""Remove any remaining '17 Rescued' occurrences from README.md, RESEARCH_NOTES_CN.md, and RESEARCH_NOTES.md."""

from pathlib import Path

files = [Path("README.md"), Path("RESEARCH_NOTES_CN.md"), Path("RESEARCH_NOTES.md")]

for f in files:
    if f.exists():
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        new_lines = []
        skip = False
        
        for l in lines:
            if "17 Rescued" in l or "17 个救回" in l:
                skip = True
                continue
            # Stop skipping when hitting next section
            if skip and (l.startswith("### ") or l.startswith("## ") or l.startswith("---") or l.startswith("| Matching Protocol")):
                skip = False
                
            if not skip:
                new_lines.append(l)
                
        f.write_text("\n".join(new_lines), encoding="utf-8")
        print(f"Cleanly removed 17 Rescued from '{f.name}'!")
