#!/usr/bin/env python3
"""Remove 'Level 3 Econometric Modeling Plan' section from README.md, RESEARCH_NOTES_CN.md, and RESEARCH_NOTES.md."""

from pathlib import Path

files = [Path("README.md"), Path("RESEARCH_NOTES_CN.md"), Path("RESEARCH_NOTES.md")]

for f in files:
    if f.exists():
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        new_lines = []
        skip = False
        
        for l in lines:
            if "Level 3 Econometric Modeling Plan" in l or "Level 3 计量模型" in l:
                skip = True
                continue
            # Stop skipping when hitting next major section ## or ---
            if skip and (l.startswith("## ") or l.startswith("---") or l.startswith("# ")):
                skip = False
            
            if not skip:
                new_lines.append(l)
                
        f.write_text("\n".join(new_lines), encoding="utf-8")
        print(f"Cleanly removed Level 3 Econometric Modeling Plan from '{f.name}'!")
