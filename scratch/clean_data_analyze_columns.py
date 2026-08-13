#!/usr/bin/env python3
"""Remove stage_origin and redundant lexicon stage columns from files inside data/analyze/ directory ONLY."""

import pandas as pd
from pathlib import Path

analyze_dir = Path("data/analyze")

# Find all CSV files in data/analyze/
csv_files = list(analyze_dir.glob("*.csv"))

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    
    # Drop stage_origin column if present
    cols_to_drop = [c for c in ['stage_origin', 'stage'] if c in df.columns]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        print(f"Dropped {cols_to_drop} from {csv_file.name}")
        
    # Save back CSV
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    # Save back XLSX matching name
    xlsx_file = csv_file.with_suffix(".xlsx")
    df.to_excel(xlsx_file, index=False)
    print(f"Updated {xlsx_file.name}")

print("\nSuccessfully cleaned all files in data/analyze/ directory!")
