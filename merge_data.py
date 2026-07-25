import os
import re
import pandas as pd

DATA_DIR = r"c:\Users\pengy\OneDrive\Desktop\Low-Altitude\02-07-2025-TripAdvisor"
RAW_OUTPUT = r"c:\Users\pengy\OneDrive\Desktop\Low-Altitude\tripadvisor_merged_raw.csv"

def extract_tour_name(filename):
    """
    Cleans up the CSV filename to extract a human-readable Tour Name.
    e.g., '1-Kauai Deluxe Sightseeing Flight_1623_attraction_product_review_2025-02-27.csv'
          -> 'Kauai Deluxe Sightseeing Flight'
    """
    name, _ = os.path.splitext(filename)
    
    for suffix in ['_attraction', '_product', '_review', '_2025-', '_2025_']:
        if suffix in name:
            name = name.split(suffix)[0]
            
    name = re.split(r'_\d{4}-\d{2}-\d{2}', name)[0]
    name = re.split(r'_\d{8}', name)[0]
    
    cleaned = re.sub(r'^\d+\s*[-\s_]\s*(\d*\s*[-\s_]\s*)*', '', name)
    cleaned = re.sub(r'_\d+$', '', cleaned)
    cleaned = re.sub(r'-\d+$', '', cleaned)
    
    cleaned = cleaned.replace('_', ' ').strip(' -_')
    return cleaned

def main():
    print("--- Stage 1: Merging CSV Files ---")
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"Data directory not found at: {DATA_DIR}")
        
    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    print(f"Found {len(all_files)} CSV files in TripAdvisor folder.")
    
    dfs = []
    total_raw_rows = 0
    
    for filename in all_files:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='latin-1')
            
        row_count = len(df)
        total_raw_rows += row_count
        
        # Standardize column headers
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Add tour_name column
        tour_name = extract_tour_name(filename)
        df['tour_name'] = tour_name
        
        dfs.append(df)
        print(f"  Loaded: '{filename}' -> Tour: '{tour_name}' ({row_count} rows)")
        
    # Concatenate all dataframes
    merged_df = pd.concat(dfs, ignore_index=True, sort=False)
    print(f"Merged raw dataset created. Total rows combined: {len(merged_df)} (Sum of individual files: {total_raw_rows})")
    
    # Save the raw merged file
    merged_df.to_csv(RAW_OUTPUT, index=False, encoding='utf-8-sig')
    print(f"Saved raw merged dataset to: {RAW_OUTPUT}")

if __name__ == "__main__":
    main()
