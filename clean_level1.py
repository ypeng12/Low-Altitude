import os
import re
import html
import pandas as pd

RAW_INPUT = "data/cleaned_datasets/tripadvisor_merged_raw.csv"
CLEANED_LEVEL1_OUTPUT = "data/cleaned_datasets/tripadvisor_level1_cleaned.csv"
CHECK_500_OUTPUT = "data/cleaned_datasets/manual_check_500.csv"
CHECK_2000_OUTPUT = "data/cleaned_datasets/manual_check_2000.csv"

def clean_published_date(val):
    """
    Standardizes dates from 'Written Month Day, Year' or 'Month Day, Year' to 'YYYY-MM-DD'.
    """
    if pd.isna(val) or not isinstance(val, str):
        return None
    cleaned = val.replace('Written', '').strip()
    parsed = pd.to_datetime(cleaned, errors='coerce')
    if pd.notna(parsed):
        return parsed.strftime('%Y-%m-%d')
    return None

def clean_html_linebreaks(text):
    """
    Cleans HTML line breaks (<br />, <br>) to newlines and decodes HTML entities.
    """
    if pd.isna(text) or not isinstance(text, str):
        return text
    
    # Replace <br />, <br>, <br/> with newline characters
    cleaned = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    
    # Decode HTML entities like &amp; -> &, &quot; -> ", &#39; -> '
    cleaned = html.unescape(cleaned)
    
    # Normalize excessive newlines (3 or more consecutive newlines to double newlines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()

def standardize_trip_type(row):
    """
    Fills missing trip_type values using the rating_text if available,
    and maps the final values to standard categories: Couples, Family, Solo, Friends, Business, Unknown.
    """
    tt = row.get('trip_type')
    rt = row.get('rating_text')
    
    if pd.isna(tt) or str(tt).strip() == '' or str(tt).lower() == 'nan':
        if isinstance(rt, str) and '•' in rt:
            parts = rt.split('•')
            if len(parts) > 1:
                tt = parts[1].strip()
                
    if pd.isna(tt) or not isinstance(tt, str) or str(tt).strip() == '' or str(tt).lower() == 'nan':
        return 'Unknown'
        
    tt_lower = tt.lower().strip()
    if 'couple' in tt_lower:
        return 'Couples'
    elif 'family' in tt_lower:
        return 'Family'
    elif 'solo' in tt_lower:
        return 'Solo'
    elif 'friend' in tt_lower:
        return 'Friends'
    elif 'business' in tt_lower:
        return 'Business'
    else:
        return 'Unknown'

def audit_and_deduplicate(df):
    """
    Executes a multi-tier duplicate review audit and performs exact + whitespace-normalized de-duplication.
    """
    print("\n--- Duplicate Review Audit & De-duplication Process ---")
    initial_count = len(df)
    
    # 1. Exact Duplicate Audit (raw user_name + review_text)
    raw_exact_dup_count = df.duplicated(subset=['user_name', 'review_text'], keep=False).sum()
    print(f"1. Exact Duplicates Audit:")
    print(f"   - Rows sharing identical (user_name + review_text) in raw data: {raw_exact_dup_count}")

    # 2. Whitespace-Normalized De-duplication (Collapsing multiple spaces & case normalization)
    print(f"2. Performing Whitespace-Normalized De-duplication...")
    temp_user = df['user_name'].fillna('anonymous_user')
    temp_norm_text = df['review_text'].astype(str).str.lower().str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # Identify near-duplicates caught by whitespace normalization before dropping (e.g. Harry M case)
    exact_mask = df.duplicated(subset=['user_name', 'review_text'], keep='first')
    norm_mask = pd.Series(list(zip(temp_user, temp_norm_text)), index=df.index).duplicated(keep='first')
    near_dup_count = (norm_mask & ~exact_mask).sum()
    print(f"   - Near-duplicates caught via whitespace normalization: {near_dup_count}")
    
    # Perform actual deduplication
    df_dedup = df.loc[~norm_mask].copy()
    removed_count = initial_count - len(df_dedup)
    print(f"   - Total duplicate rows removed: {removed_count}")
    print(f"   - Remaining clean rows after de-duplication: {len(df_dedup)}")

    # 3. Same-User / Same-Date Rewrite Audit (Identical user, title, and publication date)
    same_user_date_dup = df_dedup[df_dedup.duplicated(subset=['user_name', 'review_title', 'published_date'], keep=False)]
    print(f"3. Same-User / Same-Date Rewrite Audit:")
    print(f"   - Rewritten review versions posted on same date by same user: {len(same_user_date_dup)} rows")

    # 4. Multi-Product Review Audit (High-frequency users reviewing multiple tours)
    user_counts = df_dedup['user_name'].value_counts()
    multi_users = user_counts[user_counts > 1]
    print(f"4. High-Frequency Traveler Audit:")
    print(f"   - Distinct users reviewing multiple tour products: {len(multi_users)}")
    print(f"   - Total reviews contributed by multi-product reviewers: {df_dedup['user_name'].isin(multi_users.index).sum()}")

    return df_dedup

def main():
    print("--- Stage 2: Performing Level 1 Cleaning ---")
    if not os.path.exists(RAW_INPUT):
        raise FileNotFoundError(f"Raw merged input file not found at: {RAW_INPUT}")
        
    df = pd.read_csv(RAW_INPUT)
    initial_rows = len(df)
    print(f"Loaded raw dataset from: {RAW_INPUT} ({initial_rows} rows)")
    
    # 1. Drop unnecessary administrative columns
    cols_to_drop = ['user_profile', 'user_avatar', 'disclaimer']
    existing_drops = [c for c in cols_to_drop if c in df.columns]
    df_clean = df.drop(columns=existing_drops)
    print(f"1. Dropped administrative columns: {existing_drops}")
    
    # 2. Drop missing core fields (review_text, rating)
    print(f"2. Validating core required fields (review_text, rating)...")
    before_core_drop = len(df_clean)
    df_clean = df_clean.dropna(subset=['review_text', 'rating'])
    print(f"   - Rows dropped due to missing rating/review: {before_core_drop - len(df_clean)}")
    
    # 3. Clean HTML line breaks (<br />) and decode HTML entities
    print("3. Cleaning HTML linebreaks (<br />) and decoding HTML entities...")
    df_clean['review_text'] = df_clean['review_text'].apply(clean_html_linebreaks)
    if 'review_title' in df_clean.columns:
        df_clean['review_title'] = df_clean['review_title'].apply(clean_html_linebreaks)
        
    # 4. Standardize ratings to 1-5 integer scale
    print("4. Standardizing ratings (1-5 integer range)...")
    df_clean['rating'] = pd.to_numeric(df_clean['rating'], errors='coerce')
    df_clean = df_clean.dropna(subset=['rating'])
    df_clean['rating'] = df_clean['rating'].astype(int)
    df_clean = df_clean[(df_clean['rating'] >= 1) & (df_clean['rating'] <= 5)]
    print(f"   - Valid rating rows retained: {len(df_clean)}")
    
    # 5. Standardize publication date to YYYY-MM-DD
    print("5. Standardizing review publication dates to YYYY-MM-DD...")
    df_clean['published_date'] = df_clean['published_date'].apply(clean_published_date)
    unparsed_dates = df_clean['published_date'].isna().sum()
    print(f"   - Unparsed dates remaining: {unparsed_dates}")
    
    # 6. Extract and standardize trip_type categories
    print("6. Standardizing traveler trip types...")
    df_clean['trip_type'] = df_clean.apply(standardize_trip_type, axis=1)
    trip_type_counts = df_clean['trip_type'].value_counts()
    print("   - Trip type breakdown:")
    for category, count in trip_type_counts.items():
        print(f"     * {category}: {count}")
        
    # 7. Convert CDN photo URLs into binary indicator has_photo
    if 'photos' in df_clean.columns:
        print("7. Extracting photo attachment feature (has_photo binary indicator)...")
        df_clean['has_photo'] = df_clean['photos'].apply(lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0)
        df_clean = df_clean.drop(columns=['photos'])
        
    # 8. Multi-tier Duplicate Audit & De-duplication
    df_clean = audit_and_deduplicate(df_clean)
    
    # Select and order final output columns
    expected_cols = [
        'tour_name', 'user_name', 'user_location', 'rating', 'rating_text', 
        'review_title', 'review_text', 'trip_type', 'helpful_votes', 'has_photo', 'published_date'
    ]
    final_cols = [c for c in expected_cols if c in df_clean.columns]
    df_clean = df_clean[final_cols]
    
    print(f"\n==================================================")
    print(f"Level 1 cleaning completed successfully!")
    print(f"Final Clean Dataset: {len(df_clean)} rows (Removed {initial_rows - len(df_clean)} raw rows total)")
    print(f"==================================================")
    
    # Save Level 1 cleaned CSV output
    df_clean.to_csv(CLEANED_LEVEL1_OUTPUT, index=False, encoding='utf-8-sig')
    print(f"Saved Level 1 cleaned dataset to:\n  -> {CLEANED_LEVEL1_OUTPUT}")
    
    # 9. Generate Reproducible Random Manual Check Samples
    print("\n--- Stage 3: Generating Random Manual Check Samples ---")
    total_rows = len(df_clean)
    
    # Sample 500
    sample_500_size = min(500, total_rows)
    df_500 = df_clean.sample(n=sample_500_size, random_state=42)
    df_500.to_csv(CHECK_500_OUTPUT, index=False, encoding='utf-8-sig')
    print(f"Saved 500-review sample for manual audit to:\n  -> {CHECK_500_OUTPUT}")
    
    # Sample 2000
    sample_2000_size = min(2000, total_rows)
    df_2000 = df_clean.sample(n=sample_2000_size, random_state=42)
    df_2000.to_csv(CHECK_2000_OUTPUT, index=False, encoding='utf-8-sig')
    print(f"Saved 2000-review sample for manual audit to:\n  -> {CHECK_2000_OUTPUT}")

if __name__ == "__main__":
    main()
