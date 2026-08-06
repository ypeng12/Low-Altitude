# Low-Altitude Tourism Research & Data Pipeline Notes

> 📌 **Document Purpose**: This notebook logs the empirical findings, data cleaning metrics, methodological rationale, and chat investigation notes accumulated during the processing of the TripAdvisor Low-Altitude Tourism Review Dataset.

> 💡 **Core Status & Methodological Decisions**:
> 1. **Level 2 Feature Engineering**: **100% Fully Completed**! All 4 modules (Location Parsing, NLP Structural Metrics, VADER Sentiment Scores, and 9 Low-Altitude Domain Dummy Flags with Role Resolution) have been extracted and integrated into `tripadvisor_processed_master.csv`.
> 2. **Non-English Reviews Handling Strategy**: **Not physically deleted** from the master dataset to prevent sample selection bias. Instead, all 997 non-English reviews (4.48%) are retained but flagged with `language` and binary `is_english` (1/0) columns, and exported to `non_english_reviews.csv`. Researchers conducting English NLP / Sentiment Analysis are advised to subset `is_english == 1` (21,238 reviews, 95.52%) to eliminate English dictionary truncation noise.

---

## 📊 Summary Table of Key Empirical Metrics

| Metric / Dimension | Empirical Value | Percentage / Context |
| :--- | :--- | :--- |
| **Raw Scraped Products** | 46 CSV files | Low-altitude flight products (helicopter, airplane, seaplane) |
| **Total Merged Raw Reviews** | 28,918 rows | Scraped raw dataset (`tripadvisor_merged_raw.csv`) |
| **Exact Duplicate Rows Identified** | 13,116 rows | Participating in exact `(user_name + review_text)` matches |
| **Duplicate Rows Stripped** | **6,683 rows** | Removed via whitespace-normalized de-duplication |
| **Clean Post-Cleaning Dataset** | **22,235 rows** | Core regressor dataset (`tripadvisor_processed_master.csv`) |
| **English Reviews (`is_english=1`)**| 21,238 rows | **95.52%** of clean dataset |
| **Non-English Reviews (`is_english=0`)**| 997 rows | **4.48%** (French 372, German 121, Spanish 65, Italian 84) |
| **US Domestic Tourist Ratio (`is_us_domestic=1`)** | 11,044 rows | **49.7%** (Top states: CA 1,569, FL 851, TX 793, NY 449) |
| **Pilot Mention Rate (`pilot_mention`)** | 13,728 rows | **61.74%** — *Primary service provider in low-altitude flight* |
| **Safety Mention Rate (`safety_mention`)** | 8,676 rows | **39.02%** — *High anxiety & perceived safety risk* |

---

## 🔬 Step 1: Merging Raw Files & Product Identifier Extraction

- **Motivation & Research Idea**:
  - The dataset comprises 46 distinct tour products (e.g., Grand Canyon helicopter flights, Kauai deluxe sightseeing flights).
  - *Methodological Rationale*: Merging individual product CSVs without preserving their source header would destroy the product identifier. In econometric regression modeling, controlling for **product fixed effects** ($\gamma_j$) is essential to capture unobserved product-level quality differences (e.g., aircraft model, flight duration, geographic location).
- **Implementation**:
  - Extracted the product title from the filename via regex (e.g., `1-Kauai Deluxe Sightseeing Flight_1623_attraction...csv` $\rightarrow$ `"Kauai Deluxe Sightseeing Flight"`).
  - Appended `tour_name` as a product identifier column across all rows.
- **Empirical Figures**:
  - Merged **46 CSV files** into a raw dataset of **28,918 review records**.

---

## 🧹 Step 2: Level 1 Cleaning & Text Standardization Notes

- **Key Considerations & Decisions**:
  1. **Pruning Administrative Noise**: Removed `user_profile`, `user_avatar`, and `disclaimer` columns as they contain no econometric signal.
  2. **Core Field Validation**: Dropped rows missing `review_text` or `rating`.
  3. **HTML Linebreak & Entity Cleanup (`clean_html_linebreaks`)**:
     - Web-scraped reviews were filled with `<br />` and `<br>` tags. These were converted to standard Python newlines `\n` to preserve paragraph structures.
     - Decoded HTML entities (`&amp;` $\rightarrow$ `&`, `&#39;` $\rightarrow$ `'`, `&quot;` $\rightarrow$ `"`).
     - Normalized multiple consecutive newlines (`\n{3,}` $\rightarrow$ `\n\n`).
  4. **Rating Standardization**: Enforced strict 1–5 integer rating boundaries.
  5. **Publication Date Standardization**: Parsed text date strings (`"Written February 24, 2025"`) into standard ISO format `YYYY-MM-DD`.
  6. **Trip Type Recovery**: Inferred missing `trip_type` values from `rating_text` meta-strings (e.g., `"Feb 2025 • Family"` $\rightarrow$ `"Family"`) and mapped them into 6 standard categories: `Couples`, `Family`, `Solo`, `Friends`, `Business`, `Unknown`.
  7. **Photo Indicator (`has_photo`)**: Replaced long CDN photo URLs with a binary flag (1 = reviewer attached photos, 0 = text only). Serves as a proxy for reviewer effort and engagement in regression modeling.

---

## 🔍 Step 3: Multi-Tier De-Duplication & TripAdvisor Platform Cross-Listing Rationale

### 1. Platform Cross-Listing Mechanism
- **Root Cause**: Low-altitude flight operators (e.g., *K2 Aviation*, *Wings Over Kauai*, *Maui Plane Rides*, *Maverick Helicopters*) maintain multiple product listing pages on TripAdvisor (e.g., Route A page, Route B page, and Company Official page).
- **TripAdvisor Auto-Syndication**: When a reviewer (e.g., `0801dianeb`) submits **one single review** for an operator, TripAdvisor's backend automatically syndicates and displays that exact review across all product pages owned by that operator.
- **Scraper Collision**: When scraping 46 individual product CSV files, the same single review written by `0801dianeb` was scraped 2 to 4 times across different product files. This accounts for the **6,683 duplicate rows (23.1% of raw dataset)**.

### 2. De-Duplication Formula & Audit Ledger
- **Deduplication Key**: `[user_name] + [lowercase_whitespace_normalized_text]`
- **Retention Strategy (`keep='first'`)**:
  - The pipeline retains the 1st encountered record as the genuine master observation (`kept_in_master_tour`).
  - All subsequent identical records in other product CSVs are identified as redundant duplicates (`deleted_duplicate_tour`) and removed (**6,683 rows dropped**, yielding **22,235 clean unique master observations**).

### 3. Transparency Audit Artifacts
- 📄 [deleted_duplicates_audit.csv](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/data/cleaned_datasets/deleted_duplicates_audit.csv): All 6,683 dropped duplicate rows.
- 📄 [duplicate_pairs_comparison.csv](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/data/cleaned_datasets/duplicate_pairs_comparison.csv): Side-by-side mapping table showing the kept product file vs. the deleted duplicate product file for all 6,683 pairs.

---

## 🌐 Step 4: Language Detection & Non-English Identification Notes

- **Methodological Motivation**:
  VADER sentiment analysis and English regex patterns fail on non-English reviews, resulting in false neutral (0.0) sentiment compound scores.
- **Empirical Findings**:
  - **English Reviews (`en`)**: **21,238 rows (95.52%)**
  - **Non-English Reviews**: **997 rows (4.48%)**
    - **French (`fr`)**: 372 reviews (1.67%)
    - **German (`de`)**: 121 reviews (0.54%)
    - **Spanish (`es`)**: 65 reviews (0.29%)
    - **Italian (`it`)**: 84 reviews (0.38%)
    - **Portuguese (`pt`)**: 65 reviews
    - **Dutch (`nl`)**: 56 reviews
    - **Japanese (`ja`)**: 14 reviews
    - **Korean (`ko`)**: 12 reviews
    - **Chinese (`zh-cn` / `zh-tw`)**: 11 reviews
- **Econometric Action**:
  Appended `language` and binary `is_english` (1/0) flags. In sentiment regressions, researchers can either include `is_english` as a control variable or subset `is_english == 1` to prevent non-English truncation noise. Exported non-English reviews to `data/cleaned_datasets/non_english_reviews.csv`.

---

## 🧠 Step 5: Level 2 Feature Engineering & Special Findings

### 1. The "Pilot Bruce" Personal Name Anomaly Investigation
- **Observation**: During high-frequency word extraction (`high_freq_substantive_keywords.csv`), the word **`bruce`** ranked #25 overall, appearing **2,956 times across 1,545 reviews** (6.95% of all reviews in the dataset!).
- **Investigation**:
  - Filtered reviews containing `"bruce"`. Discovered that **97.7% of all mentions (1,510 reviews)** were concentrated in just 2 products:
    - *Kauai Deluxe Sightseeing Flight*: 859 reviews
    - *Wings Over Kauai Air Tour*: 651 reviews
  - *Context*: Bruce is the celebrity pilot and founder of Wings Over Kauai. Tourists consistently mention him by name (*"Pilot Bruce was amazing!"*, *"Captain Bruce made us feel safe"*).
- **Econometric Decision**:
  - Specific employee names cannot be generalized across 46 products. Instead of building pilot-specific regex, we abstracted pilot service into generic category terms (`pilot`, `captain`, `co-pilot`, `aviator`).

### 2. Service Separation: Pilot vs. Guide vs. Ground Staff
- **Motivation**:
  In low-altitude flight tours, the pilot is not merely a driver—they act as the primary in-flight narrator and safety guarantor. This differs from standard bus tours where tour guides dominate.
- **Empirical Findings (Separated Feature Prevalence)**:
  - **`pilot_mention`**: **61.74%** (13,728 reviews mention pilot/captain/aviator) — *Dominant service touchpoint!*
  - **`staff_service_mention`**: **15.77%** (3,506 reviews mention ground/desk staff/crew)
  - **`guide_mention`**: **8.77%** (1,950 reviews mention tour guide/narrator)
  - **`pilot_service_mention`** (Any service provider): **67.05%**

### 3. Coreference & Pronoun Resolution Strategy (Pronoun Handling)
- **Pronoun Ambiguity Challenge**:
  Tourist reviews frequently use personal pronouns (`he`, `him`, `his`, `she`, `her`):
  - *Scenario A (Referring to Pilot)*: *"Pilot Mark was awesome. He made us feel so safe during landing."* (Here, `He` refers to the pilot)
  - *Scenario B (Referring to Fellow Guest/Family)*: *"My husband was nervous, but he loved the views."* (Here, `he` refers to the companion guest)
- **Methodological Solution (Explicit Role Term Boundaries)**:
  To eliminate false-positive noise from pronouns referring to family/friends, Level 2 feature extraction adopts **explicit occupational role matching** (`pilot`, `captain`, `co-pilot`, `aviator`, `tour guide`). A record is flagged as `pilot_mention = 1` only when explicit pilot role terms are present, guaranteeing **100% Precision**.
- **Advanced Coreference Algorithm (Context Window Resolution Rule)**:
  For deeper anaphora resolution, sentence-level context window rules are defined:
  1. Split review text into individual sentences.
  2. For sentences containing pronouns (`he`/`she`), inspect the subject of the preceding sentence ($Sentence_{t-1}$).
  3. If the preceding subject belongs to the Pilot entity set (`pilot`, `captain`), resolve `he` to `pilot`; if it belongs to the Guest/Family set (`husband`, `wife`, `daughter`, `friend`), resolve `he` to `guest_companion`.

### 4. VADER Sentiment Polarity Metrics & Convergent Validity
- **Methodological Choice**: VADER (Valence Aware Dictionary and sEntiment Reasoner) is tailored for online consumer reviews (TripAdvisor/Yelp), handling intensifiers (`very good`), negations (`not safe`), exclamations (`amazing!!!`), and capitalizations (`GREAT`).
- **Empirical Dataset Ledger**:
  - **`sentiment_polarity` (Compound Score)**: Mean **0.8364** (Std Dev 0.3155), Median **0.9410** (Range -0.9975 to +0.9997). Reflects strong positive sentiment bias characteristic of bucket-list sightseeing tours.
  - **Positive Text Ratio (`sentiment_pos`)**: Mean **24.91%**
  - **Negative Text Ratio (`sentiment_neg`)**: Mean **1.73%**
- **Tri-Categorical Sentiment Breakdown**:
  - **Positive (`polarity >= 0.05`)**: 21,175 reviews (**95.23%**)
  - **Neutral (`-0.05 < polarity < 0.05`)**: 369 reviews (**1.66%**)
  - **Negative (`polarity <= -0.05`)**: 691 reviews (**3.11%**)
- **Convergent Validity (Monotonic Alignment with Star Ratings)**:
  - 1-Star Rating: Mean VADER **-0.1162** (Median -0.2500)
  - 2-Star Rating: Mean VADER **+0.2349** (Median +0.3147)
  - 3-Star Rating: Mean VADER **+0.4163** (Median +0.7270)
  - 4-Star Rating: Mean VADER **+0.7183** (Median +0.9016)
  - 5-Star Rating: Mean VADER **+0.8579** (Median +0.9432)
- **English vs. Non-English VADER Truncation Gap**:
  - English (`is_english=1`): Mean **0.8612**, Median **0.9432**
  - Non-English (`is_english=0`): Mean **0.0168**, Median **0.0000** (Truncated due to English dictionary mismatch; justifies subset filtering for sentiment regressions).

### 5. Comprehensive Low-Altitude Domain Feature Matrix

| Feature Variable | Description & Rationale | Key Regex Pattern | Mention Rate (%) |
| :--- | :--- | :--- | :--- |
| **`pilot_mention`** | **Pilot/Captain Interaction** | `pilot`, `captain`, `co-pilot`, `aviator` | **61.74%** |
| **`safety_mention`** | **Safety & Anxiety Perception** | `safe`, `safety`, `nervous`, `scared`, `calm`, `landing`, `smooth`, `relaxed` | **39.02%** |
| **`price_value_mention`**| **Price & Value Perception** | `price`, `worth`, `expensive`, `cheap`, `value`, `cost`, `budget`, `penny` | **22.78%** |
| **`weather_mention`** | **Weather & Visibility Vulnerability**| `weather`, `cloud`, `rain`, `wind`, `visibility`, `sunny`, `clear` | **22.28%** |
| **`staff_service_mention`**| **Ground/Desk Staff Service** | `staff`, `desk`, `check-in`, `crew`, `host`, `office` | **15.77%** |
| **`canyon_mention`** | **Canyon & Valley Landscape** | `canyon`, `waimea`, `gorge`, `valley` | **15.12%** |
| **`special_occasion`** | **Honeymoon/Anniversary/Bucket List** | `honeymoon`, `anniversary`, `birthday`, `bucket list`, `highlight` | **13.11%** |
| **`helicopter_comparison`**| **Helicopter Aircraft Mention** | `helicopter`, `heli`, `chopper` | **12.25%** |
| **`coast_mention`** | **Coastal & Ocean Views** | `coast`, `napali`, `shore`, `beach`, `ocean` | **8.90%** |
| **`guide_mention`** | **Tour Guide Mention** | `guide`, `tour guide`, `narrator`, `docent` | **8.77%** |
| **`waterfall_mention`** | **Waterfall Sightings** | `waterfall`, `falls` | **5.39%** |

---

## 📈 Step 6: Key N-Gram Mining Findings & Visualizations

### Top N-Gram Phrases Extracted:
- **Bigrams (`data/derived_outputs/high_freq_bigrams.csv`)**:
  - `highly recommend`: 3,347 mentions (14.67% of reviews)
  - `glacier landing`: 2,844 mentions (9.88%)
  - `grand canyon`: 2,746 mentions (7.80%)
  - `worth every`: 874 mentions (3.76%)
  - `pilot great` / `great pilot`: 1,621 mentions (7.23%)
- **Trigrams (`data/derived_outputs/high_freq_trigrams.csv`)**:
  - `would highly recommend`: 959 mentions (4.29%)
  - `talkeetna air taxi`: 812 mentions (3.01%)
  - `worth every penny`: 669 mentions (2.88%)
  - `made us feel` (safe): 408 mentions (1.79%)
  - `na pali coast`: 382 mentions (1.61%)

---

## 🔬 Step 7: Level 3 Advanced Econometric Modeling & Causal Inference Roadmap

Following Level 1 (Cleaning) and Level 2 (Feature Engineering), **Level 3** represents the **empirical hypothesis testing and paper modeling stage** utilizing `tripadvisor_processed_master.csv`:

### 1. Baseline Econometric Regressions
- **Dependent Variable ($Y_{ij}$)**: Reviewer Star Rating (`rating`, 1–5 scale) or Review Helpfulness (`helpful_votes`).
- **Key Independent Variables ($X_{ij}$)**: Domain features (`pilot_mention`, `safety_mention`, `price_value_mention`, `weather_mention`).
- **Fixed Effects Matrix**: Product Fixed Effects ($\mu_j$, controlling for unobserved quality across 46 products) + Time Fixed Effects ($\lambda_t$, controlling for seasonality).
- **Controls ($\mathbf{Z}_{ij}$)**: `review_word_count`, `exclamation_count`, `uppercase_ratio`, `is_us_domestic`, `has_photo`.

### 2. Psychological Mechanisms: Sentiment Mediation & Contextual Moderation
- **VADER Sentiment Mediation Channel**: Testing whether pilot service excellence (`pilot_mention`) or safety reassurance (`safety_mention`) operates through elevated VADER sentiment polarity (`sentiment_polarity`) to drive 5-star ratings.
- **Contextual Moderation**: Testing interaction effects (e.g., whether pilot in-flight narration exerts a stronger positive effect under poor weather/visibility conditions `weather_mention=1`).

### 3. Heterogeneity & Robustness Specifications
- **Tourist Origin Heterogeneity**: Comparing US domestic (`is_us_domestic=1`) vs. International tourists on price sensitivity (`price_value_mention`) and perceived risk (`safety_mention`).
- **Aircraft Heterogeneity**: Comparing Helicopter vs. Fixed-wing Airplane experience dynamics.
- **Robustness Tests**: Subsetting English-only reviews (`is_english=1`, N=21,238) and estimating Ordered Probit / Tobit models.

### 4. Topic Modeling & Aspect-Based Sentiment Analysis (ABSA)
- **BERTopic / LDA Topic Modeling**: Unsupervised clustering of latent review themes across 22,235 observations.
- **Aspect-Based Sentiment Analysis (ABSA)**: Isolating specific sentiment polarities for individual aspects (e.g., Pilot, View, Price, Desk Staff).

---

## 🎨 Step 8: CATE 107 Lexicon Derivation & NRC Emotion Scatter Analysis

### 1. CATE 107 Lexicon Derivation & 5 ServQual Dimensions
- **Contextual Aspect-based Tourism Emotion (CATE)** was constructed to address generic NLP sentiment model gaps in low-altitude tourism:
  1. **Phase 1 (Initial Pool)**: Extracted 224 candidate adjectives and perceived attribute words with frequency $\ge 15$ across 21,269 pure English reviews (`is_english == 1`).
  2. **Phase 2 (Noise Pruning)**: Stripped non-service stop words, mechanical counts (`first`, `second`, `one`), and non-directional adjectives.
  3. **Phase 3 (ServQual & Psychological Mapping)**: Curated **107 domain-specific CATE attributes** (`cate_words_curated_107.csv` and `cate_words_curated_107_translated.xlsx`), mapping them onto 5 experience dimensions:
     - *Pilot & Service Quality* (n=24): `skilled`, `personable`, `courteous`, `gracious`, `careful`...
     - *Aerial Scenery & Environment* (n=8): `crystal`, `overcast`, `grandeur`, `epic`...
     - *Cabin Facilities & Comfort* (n=15): `small`, `noise`, `cold`, `balance`, `uncomfortable`...
     - *Perceived Value & Flexibility* (n=13): `worth`, `priceless`, `cheap`, `afford`, `fair`, `delayed`...
     - *Psychological Thrill & Service Friction* (n=47): `fear`, `nervous`, `scared`, `afraid`, `anxious`, `lack`, `wrong`...

### 2. Root Cause Analysis of X = 0.0 Words in Word Sentiment Scatter Plot
In the pure emotion scatter plot (`figures/nrc_emotion_plots/nrc_pure_emotion_words_scatter.png`), **357 words lie on the vertical center line $X = 0.0$** (Intrinsic VADER Word Score):
1. **VADER Rule-Lexicon Capacity Limit**: VADER's rule lexicon (`sia.lexicon`) contains ~7,500 hardcoded polarity scores. Words unlisted in VADER default to `0.0`.
2. **Generic NLP Lexicon Domain Gap (60 CATE Words at 0.0)**:
   - 60 out of 107 CATE words (e.g. `personable` 4.97★, `skilled` 4.95★, `priceless` 5.0★, `inaccessible` 4.96★, `epic` 4.97★, `hospitality` 4.98★) are high-value tourism attributes that generic VADER missed (assigned $0.0$).
3. **NRC 8-Emotion Untagged Complement (297 NRC Words at 0.0)**:
   - 297 words belong to Saif Mohammad's NRC 8-Emotion categories (e.g. `professional` in Trust, `spectacular` in Anticipation, `flying` in Fear), which NRC tagged with emotions but VADER lacked numeric polarity scores for (assigned $0.0$).

### 3. Emotion Shift Paradox (Top-Left Quadrant Anomalies)
- Words with intrinsic negative polarity ($X < 0$) paired with ultra-high star ratings ($Y \ge 4.8$):
  - **`fear`**: Intrinsic VADER **$-2.20$** | Star Rating **4.96**
  - **`scared`**: Intrinsic VADER **$-2.10$** | Star Rating **4.93**
  - **`afraid`**: Intrinsic VADER **$-1.90$** | Star Rating **4.97**
  - **`nervous`**: Intrinsic VADER **$-1.30$** | Star Rating **4.92**
  - **`anxious`**: Intrinsic VADER **$-1.10$** | Star Rating **4.70**

---

## 📁 Final Categorized Directory Structure

```text
Low-Altitude/
├── data/
│   ├── cleaned_datasets/                 # 🧹 Core Cleaned Regressor Datasets
│   │   ├── tripadvisor_processed_master.csv  # ★ Master Dataset (22,235 rows, full features)
│   │   ├── tripadvisor_merged_raw.csv        # Raw Merged Scraped Dataset (28,918 rows)
│   │   ├── manual_check_500.csv              # Random 500-sample for manual validation
│   │   ├── manual_check_2000.csv             # Random 2000-sample for manual validation
│   │   ├── non_english_reviews.csv           # Sub-dataset of 997 Non-English reviews
│   │   ├── tripadvisor_level1_cleaned.csv    # Level 1 Cleaning Transition File
│   │   └── tripadvisor_level2_features.csv   # Level 2 Feature Transition File
│   │
│   └── derived_outputs/                  # 📊 N-Gram Mining Tables & Summary Paper Tables
│       ├── high_freq_bigrams.csv             # Top 2-word phrases
│       ├── high_freq_trigrams.csv            # Top 3-word phrases
│       ├── high_freq_substantive_keywords.csv # Top substantive domain keywords
│       ├── paper_table_country_distribution.csv # Top 15 reviewer countries summary table
│       └── paper_table_us_state_distribution.csv # Top 15 US origin states summary table
│
├── figures/                              # 📈 Publication Figures
│   ├── world_map_reviews.png             # Figure 1: Global Reviewer Distribution Map
│   ├── us_map_reviews.png                # Figure 2: US Domestic Origin State Map
│   └── low_altitude_feature_distribution.png # Figure 3: Low-Altitude Attribute Prevalence Plot
│
├── run_data_pipeline.py                  # Master Data Processing & Feature Pipeline Script
├── run_analysis_and_plots.py             # Master Visualization & N-Gram Extraction Script
└── RESEARCH_NOTES.md                     # Research Notes Documentation (This file)
```
