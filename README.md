# Low-Altitude Air Tourism: TripAdvisor Review Processing & Econometric Feature Pipeline

> 🌐 **Project Repository**: [https://github.com/ypeng12/Low-Altitude](https://github.com/ypeng12/Low-Altitude)  
> 📄 **Document Matrix**:
> - 🇬🇧 **English Research Notes & Pipeline Overview**: `README.md` (Current File) / `RESEARCH_NOTES.md`
> - 🇨🇳 **Chinese Comprehensive Lab Notes**: `RESEARCH_NOTES_CN.md`

---

## 🌟 Executive Summary & Project Overview

This repository provides an end-to-end data engineering, Natural Language Processing (NLP), and econometric analysis pipeline designed for **Low-Altitude Air Tourism (低空观光旅游)**. Collecting 28,918 raw tourist reviews across **46 low-altitude flight products** (including helicopter tours, fixed-wing aircraft sightseeing, and seaplane excursions) on TripAdvisor, this project builds a clean, publication-ready dataset tailored for top-tier tourism and econometric research (e.g., *Tourism Management*, *Journal of Travel Research*).

The pipeline addresses critical data quality issues (cross-listing duplicates, unformatted HTML, unstructured geographic strings) and extracts **domain-specific lexicons**, **continuous VADER sentiment scores**, and **NRC emotion-traveler interaction matrices** to examine consumer satisfaction, perceived risk, and service touchpoints.

```
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│     Raw UGC Scraping    │    │  Level 1 Data Cleaning  │    │  Level 2 Feature Eng.   │
│  46 Air Tour Products   │───►│ Deduplication & Parsing │───►│ Geographic / NLP / VADER│
│   (28,918 Reviews)      │    │  (22,235 Clean Master)  │    │   9 Domain Lexicons     │
└─────────────────────────┘    └─────────────────────────┘    └────────────┬────────────┘
                                                                           │
                                                                           ▼
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│ Level 3 Econometrics    │    │  NRC Emotion Integration│    │ Academic Visualizations │
│ OLS / Fixed Effects /   │◄───│ 8 Emotions x 5 Traveler │◄───│ Geo-Maps, Bigram Trees  │
│  Ordered Probit Models  │    │  Types (Orea-Giner 2022)│    │ & Mention Histograms   │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
```

---

## 🛠️ Data Processing & Pipeline Workflow

### Step 1: Raw Data Aggregation & Fixed Effect Preservation (`tour_name`)
- **Problem**: Scraping generated 46 separate CSV files (one per air tour product, e.g., `1-Kauai Deluxe Sightseeing Flight_1623...csv`). Simple concatenation loses product-level identity.
- **Solution**: Extracted standard product names via regular expressions and appended `tour_name` to preserve **Product Fixed Effects ($\mu_j$)** in econometric models.
- **Raw Total**: 28,918 observations.

### Step 2: Level 1 Basic Cleaning & Text Standardization
- **Column Pruning**: Removed administrative columns (`user_profile`, `user_avatar`, `disclaimer`).
- **HTML Unescaping & Linebreak Standardization**: Converted `<br />` tags to standard `\n`, unescaped HTML entities (`&amp;` $\rightarrow$ `&`, `&#39;` $\rightarrow$ `'`), and compressed redundant whitespace.
- **Date & Rating Normalization**: Parsed strings like `"Written February 24, 2025"` into standard `YYYY-MM-DD` and restricted ratings to integer scale `1–5`.
- **Trip Type Extraction**: Normalized missing trip types into 6 standard categories (`Couples`, `Family`, `Solo`, `Friends`, `Business`, `Unknown`).
- **Reviewer Effort Dummy (`has_photo`)**: Converted photo URLs into a binary indicator (1/0) reflecting reviewer engagement.

### Step 3: Multi-Dimensional Deduplication & Audit Ledger
- **Cross-Listing Mechanism**: TripAdvisor automatically cross-lists reviews across multiple product pages of the same vendor. This created a **23.1% duplicate rate** in scraped files.
- **Fingerprint De-duplication**: Formulated fingerprint `[user_name] + [whitespace_normalized_text]`.
- **Audit Findings**:
  - Identified 13,116 rows participating in strict duplicates.
  - Safely eliminated **6,683 duplicate copies** (`deleted_duplicates_audit.csv`).
  - Retained **22,235 clean master reviews** (`tripadvisor_processed_master.csv`).
  - Preserved multi-product reviews from 1,759 legitimate repeat tourists evaluating distinct air tour activities.

### Step 4: Language Detection & Non-English Subsetting
- **Language Breakdown**:
  - **English Reviews (`is_english=1`)**: **21,238 (95.52%)** — Primary sample for English VADER/NLP models.
  - **Non-English Reviews (`is_english=0`)**: **997 (4.48%)** — French (372), German (121), Spanish (65), Italian (84), Chinese (31). Exported separately to `non_english_reviews.csv` to prevent sample selection bias while avoiding VADER false zeros.

### Step 5: Level 2 Deep Feature Engineering

#### 1. Structured Geographic Location Parsing (`parse_location`)
- Parsed messy location strings (e.g., `"Hot Springs, AR"`, `"Frankfort, Ohio, United States"`, `"Brisbane, Australia"`) into `user_city`, `user_state`, and `user_country`.
- Formulated **`is_us_domestic` (1/0)**: Identified **11,044 US domestic tourists (49.7%)** (Top states: CA 1,569, FL 851, TX 793, NY 449) vs. international tourists.

#### 2. Text Metrics & Polarity Scoring
- **Text Characteristics**: Computed `review_word_count`, `review_char_count`, `exclamation_count`, and `uppercase_ratio`.
- **VADER Sentiment Analysis**: Extracted continuous `sentiment_polarity` (Compound score: $-1.0$ to $+1.0$), `sentiment_pos`, and `sentiment_neg`.

#### 3. Low-Altitude Domain Lexicon (9 Binary Indicators)
Extracted domain-specific features using Regex matching:

| Feature Flag | Category | Keywords / Regular Expressions | Sample Mention Rate |
| :--- | :--- | :--- | :---: |
| **`pilot_mention`** | Service Touchpoint | `pilot`, `captain`, `co-pilot`, `aviator`, `flyer` | **61.74%** |
| **`guide_mention`** | Service Touchpoint | `guide`, `tour guide`, `narrator`, `docent`, `instructor` | **8.77%** |
| **`staff_service_mention`** | Service Touchpoint | `staff`, `desk`, `check-in`, `crew`, `host`, `office`, `agent` | **15.77%** |
| **`safety_mention`** | Perceived Risk | `safe`, `safety`, `nervous`, `scared`, `calm`, `landing`, `smooth`, `relaxed` | **39.02%** |
| **`price_value_mention`** | Perceived Value | `price`, `worth`, `expensive`, `cheap`, `value`, `cost`, `budget`, `penny` | **22.78%** |
| **`weather_mention`** | Environment | `weather`, `cloud`, `rain`, `wind`, `visibility`, `sunny`, `clear` | **22.28%** |
| **`canyon_mention`** | Scenery Aspect | `canyon`, `waimea`, `gorge`, `valley` | **15.12%** |
| **`special_occasion`** | Travel Context | `honeymoon`, `anniversary`, `birthday`, `bucket list`, `highlight` | **13.11%** |
| **`helicopter_comparison`**| Equipment | `helicopter`, `heli`, `chopper` | **12.25%** |
| **`coast_mention`** | Scenery Aspect | `coast`, `napali`, `shore`, `beach`, `ocean`, `pacific` | **8.90%** |
| **`waterfall_mention`** | Scenery Aspect | `waterfall`, `falls` | **5.39%** |

#### 4. Coreference Resolution (`coref_resolver.py`)
- Resolved pronominal ambiguity (`he`, `she`, `they`) in review text to accurately map praised or complained attributes specifically to pilots versus ground desk staff.

---

## 🎭 Emotion Analysis & NRC Integration Model

Following **Orea-Giner et al. (2022)**, emotion in tourism is not monolithic. We integrate NRC Word-Emotion Association dimensions across 5 traveler types and disaggregated touchpoints:

```
                           ┌───────────────────────────────────┐
                           │   Tourist Review Text Corpus      │
                           └─────────────────┬─────────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
          ┌─────────────────────────┐                 ┌─────────────────────────┐
          │  VADER Sentiment Score  │                 │  NRC Emotion Association│
          │ Continuous [-1.0, +1.0] │                 │  8 Psychological Dimensions│
          └────────────┬────────────┘                 └────────────┬────────────┘
                       │                                           │
                       │     (Anger, Anticipation, Disgust, Fear, │
                       │      Joy, Sadness, Surprise, Trust)       │
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    Segmented by 5 Traveler Typologies         │
                      │  (Couples, Family, Solo, Friends, Business)  │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    Service Touchpoint Disaggregation         │
                      │   (Pilots / Tour Guides / Ground Staff)      │
                      └──────────────────────────────────────────────┘
```

---

---

## 🔬 Corpus-Derived Emotion Lexicon Codebook (Master Gold Emotion Lexicon)

To avoid relying blindly on fixed external sentiment lexicons (e.g., NRC or VADER), this project implements a two-stage **corpus-derived emotion lexicon induction pipeline** tailored specifically for low-altitude air tourism.

### Lexicon Induction & Human Calibration Workflow
- **Source Corpus**: `data/cleaned_datasets/tripadvisor_level3_english_v2.csv` (21,215 clean English reviews).
- **Stage 1 Discovery ($N=500$)**: Stratified random sampling ($N=500$, Seed 42). Extracted and adjudicated **372 clean emotion terms** (`data/derived_outputs/stage_discovery_500/clean_emotion_words_500_reviews.xlsx`).
- **Stage 2 Expansion ($N=2,000$)**: Stratified random sampling ($N=2,000$, Seed 100). Screened new candidate terms beyond Stage 1 to extract **173 new clean emotion terms** (`data/derived_outputs/stage_gold_2000/clean_emotion_words_2000_reviews.xlsx`).
- **Canonical Master Gold Lexicon (`gold_emotion_lexicon_codebook.xlsx`)**: Merged Stage 1 and Stage 2 human calibration outputs to produce the **Master Gold Emotion Lexicon Codebook** (`data/derived_outputs/gold_emotion_lexicon_codebook.xlsx`), comprising **545 pure, human-calibrated emotion & appraisal terms** with 100% contextual Chinese translations and $E_1$ vs $E_2$ affect types.

### 🔍 Sentence-Contextual Screening Logic & Adjudication Rules
Every candidate term was evaluated **strictly within its exact review sentence (`example_context`)**, adhering to human-in-the-loop adjudication standards:

#### ✅ RETAINED (Gold Emotion Lexicon: `gold_emotion_lexicon_codebook.xlsx` - 545 Words)
1. **Experiencer Affective States ($E_1$)**: Direct internal emotional/psychological states felt by the tourist (*nervous*, *awe*, *secure*, *uncomfortable*, *grateful*, *happy*, *afraid*, *thrilled*, *sick*, *surprised*, *worry*, *shame*, *privilege*, *disappointment*, *miserable*, *laughing*, *soaring*).
2. **Stimulus / Service Appraisals ($E_2$)**: Subjective evaluations of air tour attributes (*scary*, *breathtaking*, *spectacular*, *smooth*, *professional*, *flawless*, *hostile*, *nerve-wracking*, *mild*, *cute*, *compliment*, *incomprehensible*, *interesting*, *informative*, *educational*, *entertaining*, *great*, *amazing*, *good*, *awesome*, *excellent*).
3. **Polysemous Affect Terms ($E_1\_E_2$)**: Terms carrying both state and appraisal values depending on sentence context (*comfortable* - *"made us feel comfortable"* [$E_1$] vs *"comfortable air tour"* [$E_2$], *fun*, *friendly*, *knowledgeable*).
4. **Codebook Annotations**: Includes 100% contextual Chinese translations (`chinese_translation`), explicit affect types (`affect_type`), aggregated 2,500-sample frequency (`frequency_2500`), review counts, and example sentence contexts.

#### ❌ PURGED (Removed Non-Emotion Log: `removed_non_emotion_words_log.xlsx` - 3,968 Words)
1. **Neutral Physical Objects, Colors & Nature**: *blue*, *silver*, *gold*, *tall*, *pine*, *gravel*, *water*, *canyon*, *helicopter*, *plane*, *pilot*, *flight*, *island*, *glacier*.
2. **Social Courtesy / Hospitality Greetings**: *thanks*, *thank*, *thanked*, *thankyou* (purged as social formality rather than felt emotion).
3. **Cognitive / Speculative Stance Words**: *think*, *thought*, *suspect*, *doubt*, *assume*, *believe*, *guess*.
4. **Neutral Structural Modifiers & Quantifiers**: *minute*, *hour*, *dollar*, *one*, *first*, *highly*, *took*, *got*, *day*, *time*.

### 📊 Mathematical Partition Completeness
$$\text{Total Human-Screened Candidate Universe (4,513)} = \text{Gold Emotion Lexicon (545)} + \text{Removed Non-Emotion Log (3,968)}$$
$$\text{Gold Lexicon (545)} \cap \text{Removed Log (3,968)} = 0 \quad (\text{100% Zero-Overlap Guaranteed Partition})$$

### 🛠️ Key Derived Outputs & Master Files
- **Master Gold Emotion Lexicon Codebook (Excel)**: [data/derived_outputs/gold_emotion_lexicon_codebook.xlsx](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/gold_emotion_lexicon_codebook.xlsx)
- **Master Gold Emotion Lexicon Codebook (CSV)**: [data/derived_outputs/gold_emotion_lexicon_codebook.csv](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/gold_emotion_lexicon_codebook.csv)
- **Master Removed Non-Emotion Log (Excel)**: [data/derived_outputs/removed_non_emotion_words_log.xlsx](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/removed_non_emotion_words_log.xlsx)
- **Master Removed Non-Emotion Log (CSV)**: [data/derived_outputs/removed_non_emotion_words_log.csv](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/removed_non_emotion_words_log.csv)

---

## 📈 Summary Data & Empirical Metrics Ledger

| Empirical Dimension | Value | Percentage / Context | Theoretical Variable Role |
| :--- | :--- | :--- | :--- |
| **Total Scraped Files** | 46 Products | Helicopter, Fixed-Wing, Seaplane | Product Heterogeneity Source |
| **Raw Merged Reviews** | 28,918 | `tripadvisor_merged_raw.csv` | Initial Scraped Universe |
| **Eliminated Duplicates** | **6,683** | Cross-listing duplicate removal | Sample Bias Elimination |
| **Clean Master Sample** | **22,235** | `tripadvisor_processed_master.csv` | **Primary Econometric Dataset** |
| **English Sample (`is_english=1`)**| 21,238 | **95.52%** | Primary NLP/VADER Sample |
| **Non-English Sample (`is_english=0`)**| 997 | **4.48%** (French 372, German 121) | Robustness / Control Sample |
| **US Domestic Tourists (`is_us_domestic=1`)** | 11,044 | **49.7%** (CA 1569, FL 851, TX 793) | Origin Heterogeneity |
| **Pilot Mention Rate (`pilot_mention`)** | 13,728 | **61.74%** | Primary Service Touchpoint |
| **Safety Mention Rate (`safety_mention`)** | 8,676 | **39.02%** | Perceived Risk Indicator |
| **Price/Value Rate (`price_value_mention`)** | 9,747 | **43.85%** | Perceived Value Indicator |

---

## 📊 Level 3 Econometric Modeling Plan

Level 3 estimates structural econometric equations leveraging Level 2 features:

### 1. Baseline Econometric Regression Models
$$\text{Rating}_{ij} = \beta_0 + \beta_1 \text{PilotMention}_{ij} + \beta_2 \text{SafetyMention}_{ij} + \beta_3 \text{PriceValue}_{ij} + \boldsymbol{\gamma} \mathbf{Z}_{ij} + \mu_j + \lambda_t + \varepsilon_{ij}$$
* **Dependent Variable ($Y_{ij}$)**: TripAdvisor Rating (`rating`, 1–5 stars) or Helpful Votes (`helpful_votes`).
* **Key Independent Variables ($X_{ij}$)**: Level 2 domain indicators (`pilot_mention`, `safety_mention`, `price_value_mention`, `weather_mention`).
* **Controls ($\mathbf{Z}_{ij}$)**: `review_word_count`, `uppercase_ratio`, `is_us_domestic`, `has_photo`.
* **Fixed Effects**: Product Fixed Effects ($\mu_j$) for 46 products and Year/Month Time Fixed Effects ($\lambda_t$).

### 2. Psychological Mechanism & VADER Sentiment Mediation
- **Mediation Model**: Testing whether pilot excellence (`pilot_mention`) or reassuring safety (`safety_mention`) drives 5-star ratings via boosting VADER continuous sentiment polarity (`sentiment_polarity`):
  $$\text{Pilot / Safety Touchpoint} \xrightarrow{\quad\text{Elevates}\quad} \text{VADER Sentiment Polarity} \xrightarrow{\quad\text{Drives}\quad} \text{Rating (5 Stars)}$$
- **Moderation Model**: Testing environmental interaction effects (e.g., *Under adverse weather/low visibility (`weather_mention=1`), does pilot communication exert a stronger positive marginal effect on tourist ratings?*).

### 3. Group Heterogeneity & Robustness
- **Origin Heterogeneity**: Comparing US domestic tourists (`is_us_domestic=1`) vs. international tourists on price sensitivity.
- **Aircraft Type**: Helicopter vs Fixed-Wing plane satisfaction drivers.
- **Robustness Checks**: Ordered Probit / Tobit estimations restricted to English sub-sample (`is_english=1`).

---

## 📁 Repository Structure & Directory Map

```text
Low-Altitude/
├── data/
│   ├── cleaned_datasets/                 # 🧹 Processed Datasets & Master Tables
│   │   ├── tripadvisor_processed_master.csv  # ★ Master Dataset (22,235 clean rows for regressions)
│   │   ├── deleted_duplicates_audit.csv      # Audit log of 6,683 removed duplicates
│   │   ├── duplicate_pairs_comparison.csv    # Pairwise comparison log of duplicates
│   │   ├── non_english_reviews.csv           # 997 Non-English review subset
│   │   ├── tripadvisor_merged_raw.csv        # Merged raw scraped dataset (28,918 rows)
│   │   ├── tripadvisor_level1_cleaned.csv    # Level 1 cleaned dataset
│   │   └── tripadvisor_level2_features.csv   # Level 2 engineered feature dataset
│   │
│   └── derived_outputs/                  # 📊 Derived N-grams & Academic Tables
│       ├── high_freq_bigrams.csv             # Top tourist N-gram bigrams
│       ├── high_freq_trigrams.csv            # Top tourist N-gram trigrams
│       ├── high_freq_substantive_keywords.csv # Substantive keyword frequency table
│       ├── paper_table_country_distribution.csv # Top 15 tourist origin countries
│       └── paper_table_us_state_distribution.csv # Top 15 US tourist origin states
│
├── figures/                              # 📈 Publication-Ready Figures
│   ├── world_map_reviews.png             # Figure 1: Global Tourist Heatmap
│   ├── us_map_reviews.png                # Figure 2: US Domestic Tourist Origin Heatmap
│   └── low_altitude_feature_distribution.png # Figure 3: Domain Feature Mention Histogram
│
├── 02-07-2025-TripAdvisor/               # 📁 Raw scraped 46 product CSV files
├── clean_level1.py                       # 🚀 Level 1 Cleaning & Deduplication Script
├── clean_level2.py                       # 🚀 Level 2 NLP, VADER & Geographic Feature Script
├── coref_resolver.py                     # 🚀 Pronoun Coreference Resolution Script
├── run_data_pipeline.py                  # 🚀 Master Data Pipeline Runner
├── run_analysis_and_plots.py             # 🚀 Visualization & Post-processing Script
├── RESEARCH_NOTES.md                     # 📝 Detailed English Research Log
├── RESEARCH_NOTES_CN.md                  # 📘 Comprehensive Chinese Research Notes
└── README.md                             # 📄 Project Overview & Main Documentation (This file)
```

---

## 💻 Quick Execution Guide

Execute the full pipeline from raw data to econometric master table and visualization figures:

```bash
# Step 1: Run full data cleaning & Level 2 feature engineering pipeline
python run_data_pipeline.py

# Step 2: Generate figures and extract N-gram frequency tables
python run_analysis_and_plots.py
```
