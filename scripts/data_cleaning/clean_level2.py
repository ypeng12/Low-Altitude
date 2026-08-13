import pandas as pd
import numpy as np
import re
import os
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

sia = SentimentIntensityAnalyzer()

# State Mapping
US_STATES_MAP = {
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA',
    'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA',
    'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA',
    'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS', 'MISSOURI': 'MO',
    'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV', 'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH',
    'OKLAHOMA': 'OK', 'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT',
    'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY',
    'DISTRICT OF COLUMBIA': 'DC', 'WASHINGTON DC': 'DC', 'PUERTO RICO': 'PR'
}
US_CODES = set(US_STATES_MAP.values())

# Popular Country Mappings
COUNTRY_ALIAS = {
    'USA': 'United States', 'US': 'United States', 'UNITED STATES OF AMERICA': 'United States',
    'UK': 'United Kingdom', 'ENGLAND': 'United Kingdom', 'SCOTLAND': 'United Kingdom', 'WALES': 'United Kingdom',
    'GREAT BRITAIN': 'United Kingdom', 'NZ': 'New Zealand', 'AUS': 'Australia', 'CAN': 'Canada',
    'UAE': 'United Arab Emirates'
}

COMMON_COUNTRIES = {
    'UNITED STATES', 'AUSTRALIA', 'UNITED KINGDOM', 'CANADA', 'NEW ZEALAND', 'GERMANY',
    'FRANCE', 'JAPAN', 'CHINA', 'BRAZIL', 'INDIA', 'ITALY', 'SPAIN', 'MEXICO', 'NETHERLANDS',
    'SWITZERLAND', 'ROMANIA', 'ISRAEL', 'SWEDEN', 'NORWAY', 'DENMARK', 'IRELAND',
    'SOUTH AFRICA', 'SINGAPORE', 'BELGIUM', 'AUSTRIA', 'PHILIPPINES', 'MALAYSIA',
    'THAILAND', 'SOUTH KOREA', 'ARGENTINA', 'CHILE', 'COLOMBIA', 'PORTUGAL', 'GREECE',
    'POLAND', 'CZECH REPUBLIC', 'HUNGARY', 'FINLAND', 'NEW CALEDONIA', 'FIJI'
}

def parse_location(loc_str):
    if not isinstance(loc_str, str) or not loc_str.strip():
        return {'user_city': None, 'user_state': None, 'user_country': 'Unknown', 'is_us_domestic': 0}
    
    loc_clean = loc_str.strip()
    parts = [p.strip() for p in loc_clean.split(',')]
    
    city = None
    state = None
    country = 'Unknown'
    is_us = 0
    
    last_part = parts[-1].upper()
    
    # 1. Single part string
    if len(parts) == 1:
        if last_part in COUNTRY_ALIAS:
            country = COUNTRY_ALIAS[last_part]
        elif last_part in COMMON_COUNTRIES:
            country = last_part.title()
        elif last_part in US_STATES_MAP:
            state = US_STATES_MAP[last_part]
            country = 'United States'
            is_us = 1
        elif last_part in US_CODES:
            state = last_part
            country = 'United States'
            is_us = 1
        else:
            city = loc_clean
            country = 'Unknown'
            
    # 2. Multi-part string e.g. "Milpitas, CA" or "Brisbane, Australia" or "Frankfort, Ohio, United States"
    else:
        # Check last part
        if last_part in COUNTRY_ALIAS:
            country = COUNTRY_ALIAS[last_part]
        elif last_part in COMMON_COUNTRIES:
            country = last_part.title()
        elif last_part in US_CODES:
            state = last_part
            country = 'United States'
            is_us = 1
        elif last_part in US_STATES_MAP:
            state = US_STATES_MAP[last_part]
            country = 'United States'
            is_us = 1
            
        # If last part was country, check second to last part for US state
        if country == 'United States' and len(parts) >= 2:
            mid_part = parts[-2].upper()
            if mid_part in US_CODES:
                state = mid_part
            elif mid_part in US_STATES_MAP:
                state = US_STATES_MAP[mid_part]
            city = parts[0]
        elif country != 'Unknown':
            city = parts[0]
            if len(parts) >= 3 and country == 'Canada':
                state = parts[-2]
        else:
            # Fallback check if last part is US state code (e.g., "Hot Springs, AR")
            if last_part in US_CODES:
                state = last_part
                country = 'United States'
                is_us = 1
                city = parts[0]
            elif last_part in US_STATES_MAP:
                state = US_STATES_MAP[last_part]
                country = 'United States'
                is_us = 1
                city = parts[0]
            else:
                city = parts[0]
                country = parts[-1].title()

    if country == 'United States':
        is_us = 1

    return {
        'user_city': city,
        'user_state': state,
        'user_country': country,
        'is_us_domestic': is_us
    }

def main():
    input_file = "tripadvisor_level1_cleaned.csv"
    output_file = "tripadvisor_level2_features.csv"
    
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} records.")
    
    # Fill missing string fields gracefully
    df['review_text'] = df['review_text'].fillna('')
    df['review_title'] = df['review_title'].fillna('')
    df['user_location'] = df['user_location'].fillna('')
    
    print("Parsing locations...")
    loc_records = df['user_location'].apply(parse_location).tolist()
    loc_df = pd.DataFrame(loc_records)
    
    df['user_city'] = loc_df['user_city']
    df['user_state'] = loc_df['user_state']
    df['user_country'] = loc_df['user_country']
    df['is_us_domestic'] = loc_df['is_us_domestic']
    
    print("Extracting NLP and Low-Altitude Experience features...")
    
    # Text metrics
    df['review_word_count'] = df['review_text'].apply(lambda x: len(x.split()))
    df['review_char_count'] = df['review_text'].apply(len)
    df['title_word_count'] = df['review_title'].apply(lambda x: len(x.split()))
    df['exclamation_count'] = df['review_text'].apply(lambda x: x.count('!'))
    df['uppercase_ratio'] = df['review_text'].apply(
        lambda x: (sum(1 for c in x if c.isupper()) / len(x)) if len(x) > 0 else 0.0
    )
    
    # VADER Sentiment Polarity
    print("Computing VADER sentiment scores...")
    sentiments = df['review_text'].apply(lambda x: sia.polarity_scores(x) if x else {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0})
    df['sentiment_polarity'] = [s['compound'] for s in sentiments]
    df['sentiment_pos'] = [s['pos'] for s in sentiments]
    df['sentiment_neg'] = [s['neg'] for s in sentiments]
    
    # Combine title and text for keyword feature extraction
    full_text = (df['review_title'] + ' ' + df['review_text']).str.lower()
    
    # Low-Altitude Experience Features (Regex / Keyword Flags)
    print("Extracting Domain-Specific Features...")
    
    # 1. Safety & Anxiety Perception
    safety_pat = r'\b(safe|safety|nervous|calm|scared|frightened|smooth|landing|reassured|comfort|comfortable|ease|relax|reassure|anxious|anxiety)\b'
    df['safety_mention'] = full_text.str.contains(safety_pat, regex=True).astype(int)
    
    # 2. Helicopter vs Airplane Comparison
    heli_pat = r'\b(helicopter|heli|chopper)\b'
    df['helicopter_comparison'] = full_text.str.contains(heli_pat, regex=True).astype(int)
    
    # 3. Price Sensitivity & Value for Money
    price_pat = r'\b(economical|cheap|expensive|price|priced|worth|dime|penny|value|cost|budget|affordable|deal)\b'
    df['price_value_mention'] = full_text.str.contains(price_pat, regex=True).astype(int)
    
    # 4. Scenery Elements
    df['coast_mention'] = full_text.str.contains(r'\b(coast|napali|na pali|shore|beach|ocean|sea|pacific)\b', regex=True).astype(int)
    df['canyon_mention'] = full_text.str.contains(r'\b(canyon|waimea|gorge|valley|canyons)\b', regex=True).astype(int)
    df['waterfall_mention'] = full_text.str.contains(r'\b(waterfall|waterfalls|falls|fall)\b', regex=True).astype(int)
    df['wildlife_mention'] = full_text.str.contains(r'\b(whale|whales|dolphin|wildlife|turtle|turtles)\b', regex=True).astype(int)
    
    # 5. Weather Sensitivity
    weather_pat = r'\b(weather|cloud|clouds|cloudy|rain|rainy|wind|windy|headwind|visibility|clear|sun|sunny|rainbow)\b'
    df['weather_mention'] = full_text.str.contains(weather_pat, regex=True).astype(int)
    
    # 6. Pilot vs Guide vs Ground Staff Interaction (Separated)
    df['pilot_mention'] = full_text.str.contains(r'\b(pilot|captain|co-pilot|aviator|flyer)\b', regex=True).astype(int)
    df['guide_mention'] = full_text.str.contains(r'\b(guide|tour guide|narrator|docent|instructor)\b', regex=True).astype(int)
    df['staff_service_mention'] = full_text.str.contains(r'\b(staff|desk|check-in|crew|host|office|agent)\b', regex=True).astype(int)
    df['pilot_service_mention'] = ((df['pilot_mention'] == 1) | (df['guide_mention'] == 1) | (df['staff_service_mention'] == 1)).astype(int)
    
    # 7. Special Travel Occasion (Honeymoon, Anniversary, High Point)
    occasion_pat = r'\b(honeymoon|anniversary|birthday|bucket list|highlight|50th|celebrat\w*|special occasion)\b'
    df['special_occasion'] = full_text.str.contains(occasion_pat, regex=True).astype(int)

    # Aircraft Type from tour_name
    tour_lower = df['tour_name'].fillna('').str.lower()
    df['aircraft_type'] = np.where(
        tour_lower.str.contains('helicopter|heli'), 'Helicopter',
        np.where(tour_lower.str.contains('plane|wings|flight|air'), 'Airplane', 'Other/Unspecified')
    )
    
    print(f"Saving Level 2 features dataset to {output_file}...")
    df.to_csv(output_file, index=False)
    print("Done! Level 2 dataset saved successfully.")
    
    # Print Quick Insights
    print("\n--- LEVEL 2 DATASET SUMMARY ---")
    print(f"Total Rows: {len(df)}")
    print(f"Top 5 Countries:\n{df['user_country'].value_counts().head(5)}")
    print(f"US Domestic Percentage: {df['is_us_domestic'].mean()*100:.1f}%")
    print(f"Top 5 US States:\n{df[df['is_us_domestic']==1]['user_state'].value_counts().head(5)}")
    print("\n--- Low-Altitude Domain Features Mention Rate ---")
    features = ['safety_mention', 'helicopter_comparison', 'price_value_mention', 
                'coast_mention', 'canyon_mention', 'waterfall_mention', 'weather_mention', 
                'pilot_mention', 'guide_mention', 'staff_service_mention', 'special_occasion']
    for f in features:
        print(f"  {f:25s}: {df[f].mean()*100:.2f}%")

if __name__ == "__main__":
    main()
