#!/usr/bin/env python3
"""Remove affect_type (E1/E2) column from all files in data/analyze/ directory."""

import pandas as pd
from pathlib import Path
import subprocess

analyze_dir = Path("data/analyze")

csv_files = list(analyze_dir.glob("*.csv"))

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    
    # Drop affect_type column if present
    if 'affect_type' in df.columns:
        df = df.drop(columns=['affect_type'])
        print(f"Dropped affect_type (E1/E2) from {csv_file.name}")
        
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    xlsx_file = csv_file.with_suffix(".xlsx")
    df.to_excel(xlsx_file, index=False)
    print(f"Updated {xlsx_file.name}")

# Format XLSX with openpyxl styling
res = subprocess.run(["python3", "scratch/format_excel_master.py"], capture_output=True, text=True)
print(res.stdout.strip())

print("\nSuccessfully removed E1/E2 (affect_type) from all files in data/analyze/!")
