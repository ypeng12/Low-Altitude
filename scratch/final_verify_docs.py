#!/usr/bin/env python3
"""Final verification and commit check for README.md and RESEARCH_NOTES_CN.md."""

from pathlib import Path
import subprocess

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

assert "15,581" in readme_text, "README.md should contain 15,581 count for Cause 1"
assert "15,581" in cn_text, "RESEARCH_NOTES_CN.md should contain 15,581 count for Cause 1"
assert "斩首" not in cn_text, "RESEARCH_NOTES_CN.md should NOT contain casual wording 斩首"

print("✅ All doc assertions passed cleanly!")

# Re-generate Chinese PDF report
res_pdf = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res_pdf.stdout.strip())
