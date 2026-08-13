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

## 🔬 Stage 1: Corpus-Derived Master Gold Emotion Lexicon Construction (Data Cleaning & Induction)

To avoid relying blindly on generic off-the-shelf sentiment lexicons (e.g., NRC, VADER, or LIWC), this project implements a 3-step **Corpus-Derived Emotion Lexicon Induction Methodology** tailored specifically for low-altitude air tourism across all **21,215 clean English tourist reviews**.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Full Clean English Corpus (N=21,215 Reviews)                               │
└────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                                         │
         ┌───────────────────────────────────────────────┼───────────────────────────────────────────────┐
         ▼                                               ▼                                               ▼
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│ Step 1: Discovery (N=500 Reviews)    │     │ Step 2: Gold Expansion (N=2,000)     │     │ Step 3: Full Completion (N=18,901)   │
│ Stratified Random Sample (Seed 42)   │     │ Stratified Random Sample (Seed 100)  │     │ Unsampled Remaining Corpus Reviews   │
│ Extracted 372 Clean Emotion Terms    │     │ Expanded 173 New Emotion Terms       │     │ Extracted 4,213 Candidate Terms      │
└──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘
                   │                                            │                                            │
                   └────────────────────────────────────────────┼────────────────────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Master Human Calibration & Typo Normalization (canonical_lemma)                                                  │
│ - Typo Normalization: suprised->surprised, exhilerating->exhilarating, aprehensive->apprehensive                    │
│ - Strict Purging Rules: Purged entity names (grand), economic price (expensive), interjections (wow/yay)        │
│ - Final Outcome: 630 Master Gold Emotion Words | 8,096 Master Purged Non-Emotion Terms (100% Zero Overlap)       │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Step-by-Step Evolution & Methodology

> [!IMPORTANT]
> **Gold Emotion Lexicon Composition Formula**:
> 1. **Initial 2,500-Review Sample Gold Lexicon ($N=2,500$)**:
>    $$\text{Stage 1 Discovery (500 Reviews: 372 Words)} + \text{Stage 2 Expansion (2,000 Reviews: 173 Words)} = \mathbf{545 \text{ Gold Words}}$$
> 2. **Master Full-Corpus Gold Lexicon ($N=21,215$)**:
>    $$\text{Initial 2,500 Sample Gold Lexicon (545 Words)} + \text{Stage Final New Words (18,901 Reviews: 63 Words)} = \mathbf{608 \text{ Master Gold Words}}$$
> 3. **Final Calibrated Master Codebook ($N=630$)**:
>    $$\text{Master Gold Lexicon (608 Words)} + \text{Fine-Grained Human Calibration Adjustments} = \mathbf{630 \text{ Master Gold Words}}$$

#### 📍 Step 1: Initial Discovery Induction ($N=500$ Sample)
- **Sampling Protocol**: Stratified random sampling ($N=500$, Seed 42) across 46 air tour products, star rating tiers ($1–5$ stars), aircraft types, and review length quartiles.
- **Output**: Extracted **372 clean emotion terms** (`data/derived_outputs/stage_discovery_500/clean_emotion_words_500_reviews.xlsx`).

#### 📍 Step 2: Gold Expansion ($N=2,000$ Sample)
- **Sampling Protocol**: Secondary stratified random sampling ($N=2,000$, Seed 100, incorporating 1,814 new unsampled reviews).
- **Output**: Added **173 new clean emotion terms** (`data/derived_outputs/stage_gold_2000/clean_emotion_words_2000_reviews.xlsx`), establishing a 545-word sample lexicon.

#### 📍 Step 3: Corpus-Wide Completion ($N=18,901$ Unsampled Reviews)
- **Scope**: Scanned all remaining 18,901 unsampled reviews ($21,215 - 2,314 = 18,901$) to eliminate sampling oversight.
- **Output**: Extracted **4,213 candidate terms** (freq $\ge 3$), identifying 63 new emotion terms (`data/derived_outputs/stage_final/clean_new_emotion_words_18901.xlsx`).

#### 📍 Step 4: Human-in-the-Loop Fine Adjudication & Typo Normalization (`canonical_lemma`)
- **Typo Normalization**: Standardized typos directly to standard dictionary lemmas via `canonical_lemma` (*suprised $\rightarrow$ surprised*, *exhilerating $\rightarrow$ exhilarating*, *worries $\rightarrow$ worry*).
- **Retained Criteria (630 Words)**: Included $E_1$ Experiencer Affect (*nervous, afraid, happy, thrilled*), $E_2$ Stimulus Appraisals (*scary, spectacular, smooth, professional*), and Aesthetic Emotions (*breathtakingly, sublime*).
- **Purged Criteria (8,096 Words)**: Excluded entity names (*grand* for Grand Canyon), economic price ratings (*expensive, overpriced*), informal interjections (*wow, yay*), procedural service efficiency (*knowledgeable, informative, timely*), and physical flight turbulence (*choppy*).

---

## 📊 Stage 2: Generic Lexicon Audit & NRC Framework Classification (Data Analysis & Comparative Audit)

In **Stage 2 Data Analysis** (conducted in `data/analyze/`), we mapped our **630 Master Gold Emotion Terms** against the **NRC Emotion Lexicon** (Mohammad & Turney) to evaluate generic lexicon coverage gaps and categorize our domain codebook under the NRC theoretical framework.

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

### 1. NRC Theoretical Framework Classification & Structural Breakdown ($N=630$ Words)

```text
Master Gold Emotion Codebook (N = 630 Words)
│
├── 1️⃣ Mapped to NRC 8-Emotion Categories ────────── 286 words (45.40%) ⭐ (Recommended)
│       (via Canonical Lemma Normalization, rescuing 17 inflected/typo words)
│
├── 2️⃣ Mapped to Positive/Negative Polarity Only ─── 72 words (11.43%)
│       (e.g., worth, interesting, cool, calm, fortunate, pristine)
│
└── 3️⃣ Completely MISSED by NRC Lexicon ────────── 272 words (43.17%)
        (e.g., great, amazing, best, awesome, fantastic, incredible, breathtaking, stunning, awe)
```

$$\text{Total Master Gold Codebook (630)} = 286 \text{ (8-Emotions)} + 72 \text{ (Polarity Only)} + 272 \text{ (NRC Misses)}$$

---

### 2. Dual-Layer Matching Protocol: Raw Exact Match vs. Canonical Lemma Match

```python
import pandas as pd
from nrclex import NRCLex

# Load 630 Master Gold Emotion Codebook
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

# 1. Raw Exact String Match (Unnormalized)
raw_8 = sum(1 for row in df_gold.itertuples() if len(set(nrc_dict.get(str(row.word).lower().strip(), [])) & NRC8) > 0)

# 2. Canonical Lemma Match (Normalized via canonical_lemma)
lemma_8 = sum(1 for row in df_gold.itertuples() if len(set(nrc_dict.get(str(row.canonical_lemma).lower().strip(), [])) & NRC8) > 0 or len(set(nrc_dict.get(str(row.word).lower().strip(), [])) & NRC8) > 0)
```

| Matching Protocol | NRC 8-Emotion Match Count | Only Polarity Count | Completely Missed Count | Total Codebook Universe | Key Methodological Takeaway |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Raw Exact Match (Unnormalized)** | 269 words (42.70%) | 72 words (11.43%) | 289 words (45.87%) | 630 words | Plurals (-s), past participles (-ed), and typos are lost as "unmapped". |
| **Canonical Lemma Match (Normalized)** ⭐ | **286 words (45.40%)** | **72 words (11.43%)** | **272 words (43.17%)** | **630 words** | **Rescues 17 true 8-emotion terms via lemma root mapping! (Recommended)** |

---

### 3. 17 Rescued Emotion Terms via Canonical Lemma Normalization

| Raw Token in Review (`word`) | Normalized Root Lemma (`canonical_lemma`) | Review Freq ($N=21,215$) | Rescued NRC 8-Emotion Categories | Why Raw String Matching Failed |
| :--- | :--- | :---: | :--- | :--- |
| **`worries`** | **`worry`** | 38 | `fear, anticipation, sadness` | Raw NRC misses plural *-es* suffix |
| **`surprises`** | **`surprise`** | 21 | `fear, joy, surprise` | Raw NRC misses plural *-s* suffix |
| **`cherished`** | **`cherish`** | 8 | `trust, anticipation, joy, surprise` | Raw NRC misses past participle *-ed* |
| **`hates`** | **`hate`** | 5 | `anger, fear, disgust, sadness` | Raw NRC misses verb inflection *-s* |
| **`hated`** | **`hate`** | 5 | `anger, fear, disgust, sadness` | Raw NRC misses past tense *-ed* |
| **`marveled`** | **`marvel`** | 5 | `surprise` | Raw NRC misses past tense *-ed* |
| **`dreaded`** | **`dread`** | 4 | `fear, anticipation` | Raw NRC misses participle *-ed* |
| **`dreading`** | **`dread`** | 4 | `fear, anticipation` | Raw NRC misses participle *-ing* |
| **`scaring`** | **`scare`** | 3 | `anger, fear, anticipation, surprise` | Raw NRC misses participle *-ing* |
| **`horribly`** | **`horrible`** | 3 | `anger, fear, disgust` | Raw NRC misses adverbial *-ly* |
| **`apprehensions`** | **`apprehension`** | 3 | `fear` | Raw NRC misses noun plural *-s* |
| **`suprise`** | **`surprise`** | 5 | `fear, joy, surprise` | Raw NRC misses typo variant (missing r) |
| **`suprised`** | **`surprised`** | 4 | `surprise` | Raw NRC misses typo variant |
| **`dissapointed`** | **`disappointed`** | 8 | `anger, disgust, sadness` | Raw NRC misses typo variant |
| **`aprehensive`** | **`apprehensive`** | 3 | `fear, anticipation` | Raw NRC misses typo variant |
| **`disappointingly`**| **`disappointed`** | 3 | `anger, disgust, sadness` | Raw NRC misses adverbial derivation |
| **`lucked`** | **`lucky`** | 86 | `joy, surprise` | Raw NRC misses verbalized inflection |

---

### 4. 4 Root Causes of Generic NRC Lexicon Gaps ($N=272$ Missed Words)

1. **Morphological & Participle Omissions (50.00% of Misses)**:
   - **Participle Forms (-ing / -ed)**: 78 words (28.68%), e.g., *amazing, loved, breathtaking, stunning, impressed, inspiring, relaxed, scared, thrilling*.
   - **Adverbs & Superlatives (-ly, -est, -er)**: 58 words (21.32%), e.g., *best (3,420), better (1,585), incredibly (315), perfectly (175), cheaper, smoother, safely*.
   - *Finding*: Generic NRC lexicons lack morphological derivation rules, causing massive loss of participle emotion adjectives.

2. **Omission of Modern Online Tourism Colloquial Superlatives (44.85% of Misses)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), incredible (1,612), nice (1,794), fabulous, phenomenal, unbeatable, top-notch*.
   - *Deep Cause*: NRC 2012 seed vocabulary prioritized formal written English. Modern TripAdvisor reviewers rely heavily on colloquial high-arousal superlatives (*great, awesome, fantastic*), causing widespread generic lexicon failure in online review contexts.

3. **Absence of Low-Altitude Aerial Visual Awe & Aesthetic Emotions (3.31% of Misses)**:
   - **Key Terms**: *breathtaking (1,346), stunning (552), sublime (291), scenic (400), surreal (98), majestic, panoramic, spellbinding, mesmerizing, awe (304)*.
   - *Deep Cause*: Low-altitude air tourism is uniquely defined by **Aerial Visual Awe**, a domain-specific aesthetic emotion completely absent from generic news or conversational lexicons.

4. **Absence of Flight Perceived Risk & Somatic Symptoms (1.84% of Misses)**:
   - **Key Terms**: *claustrophobia, jitters, airsick, phobia, unnerving*.
   - *Deep Cause*: Flight vibration, confined cabin space, and altitude suspense trigger somatic anxiety and perceived risk reactions specific to aviation tourism.

---

### 5. Master Gold Emotion Lexicon Scatter Plot (VADER Valence vs. Tourist Rating)

![Master Gold VADER NRC Scatter Plot](data/analyze/master_gold_vader_nrc_scatter.png)

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



### 📊 7. NRC Lexicon Mapping & Comparative Audit ($N=630$ Words)

To validate the theoretical superiority of our **Corpus-Derived Gold Emotion Lexicon** over generic off-the-shelf lexicons, we mapped all **630 Master Gold Emotion Terms** against the **NRC Emotion Lexicon** (Mohammad & Turney):

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

#### 🔬 Dual-Layer Matching Protocol: Raw Exact Match vs. Canonical Lemma Match

In generic NLP pipelines, matching raw unnormalized words against static dictionaries leads to severe misclassification due to plurals, verb inflections, and typos. We compared **Raw String Matching** against our **Canonical Lemma Normalization Protocol**:

```python
import pandas as pd
from nrclex import NRCLex

# Load 630 Master Gold Emotion Codebook
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

# 1. Raw Exact String Match (Unnormalized)
raw_8 = sum(1 for row in df_gold.itertuples() if len(set(nrc_dict.get(str(row.word).lower().strip(), [])) & NRC8) > 0)

# 2. Canonical Lemma Match (Normalized via canonical_lemma)
lemma_8 = sum(1 for row in df_gold.itertuples() if len(set(nrc_dict.get(str(row.canonical_lemma).lower().strip(), [])) & NRC8) > 0 or len(set(nrc_dict.get(str(row.word).lower().strip(), [])) & NRC8) > 0)
```

| Matching Protocol | NRC 8-Emotion Match Count | Only Polarity Count | Completely Missed Count | Total Codebook Universe | Key Methodological Takeaway |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Raw Exact Match (Unnormalized)** | 269 words (42.70%) | 72 words (11.43%) | 289 words (45.87%) | 630 words | Plurals (-s), past participles (-ed), and typos are lost as "unmapped". |
| **Canonical Lemma Match (Normalized)** ⭐ | **286 words (45.40%)** | **72 words (11.43%)** | **272 words (43.17%)** | **630 words** | **Rescues 17 true 8-emotion terms via lemma root mapping! (Recommended)** |

$$\text{Total Master Gold Codebook (630)} = 286 \text{ (8-Emotions)} + 72 \text{ (Polarity Only)} + 272 \text{ (NRC Misses)}$$

---

#### 💡 17 Rescued Emotion Terms via Canonical Lemma Normalization

By instituting our **Canonical Lemma Normalization Protocol**, 17 inflected plurals, past participles, and typo variants were mapped back to their dictionary root lemmas, successfully recovering their 8-emotion tags:

| Raw Token in Review (`word`) | Normalized Root Lemma (`canonical_lemma`) | Review Freq ($N=21,215$) | Rescued NRC 8-Emotion Categories | Why Raw String Matching Failed |
| :--- | :--- | :---: | :--- | :--- |
| **`worries`** | **`worry`** | 38 | `fear, anticipation, sadness` | Raw NRC misses plural *-es* suffix |
| **`surprises`** | **`surprise`** | 21 | `fear, joy, surprise` | Raw NRC misses plural *-s* suffix |
| **`cherished`** | **`cherish`** | 8 | `trust, anticipation, joy, surprise` | Raw NRC misses past participle *-ed* |
| **`hates`** | **`hate`** | 5 | `anger, fear, disgust, sadness` | Raw NRC misses verb inflection *-s* |
| **`hated`** | **`hate`** | 5 | `anger, fear, disgust, sadness` | Raw NRC misses past tense *-ed* |
| **`marveled`** | **`marvel`** | 5 | `surprise` | Raw NRC misses past tense *-ed* |
| **`dreaded`** | **`dread`** | 4 | `fear, anticipation` | Raw NRC misses participle *-ed* |
| **`dreading`** | **`dread`** | 4 | `fear, anticipation` | Raw NRC misses participle *-ing* |
| **`scaring`** | **`scare`** | 3 | `anger, fear, anticipation, surprise` | Raw NRC misses participle *-ing* |
| **`horribly`** | **`horrible`** | 3 | `anger, fear, disgust` | Raw NRC misses adverbial *-ly* |
| **`apprehensions`** | **`apprehension`** | 3 | `fear` | Raw NRC misses noun plural *-s* |
| **`suprise`** | **`surprise`** | 5 | `fear, joy, surprise` | Raw NRC misses typo variant (missing r) |
| **`suprised`** | **`surprised`** | 4 | `surprise` | Raw NRC misses typo variant |
| **`dissapointed`** | **`disappointed`** | 8 | `anger, disgust, sadness` | Raw NRC misses typo variant |
| **`aprehensive`** | **`apprehensive`** | 3 | `fear, anticipation` | Raw NRC misses typo variant |
| **`disappointingly`**| **`disappointed`** | 3 | `anger, disgust, sadness` | Raw NRC misses adverbial derivation |
| **`lucked`** | **`lucky`** | 86 | `joy, surprise` | Raw NRC misses verbalized inflection |

---

#### 🔍 4 Root Causes of NRC Generic Lexicon Gaps ($N=272$ Missed Words):

1. **Morphological & Participle Omissions (50.00% of Misses)**:
   - **Participle Forms (-ing / -ed)**: 78 words (28.68%), e.g., *amazing, loved, breathtaking, stunning, impressed, inspiring, relaxed, scared, thrilling*.
   - **Adverbs & Superlatives (-ly, -est, -er)**: 58 words (21.32%), e.g., *best (3,420), better (1,585), incredibly (315), perfectly (175), cheaper, smoother, safely*.
   - *Finding*: Generic NRC lexicons lack morphological derivation rules, causing massive loss of participle emotion adjectives.

2. **Omission of Modern Online Tourism Colloquial Superlatives (44.85% of Misses)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), incredible (1,612), nice (1,794), fabulous, phenomenal, unbeatable, top-notch*.
   - *Deep Cause*: NRC 2012 seed vocabulary prioritized formal written English. Modern TripAdvisor reviewers rely heavily on colloquial high-arousal superlatives (*great, awesome, fantastic*), causing widespread generic lexicon failure in online review contexts.

3. **Absence of Low-Altitude Aerial Visual Awe & Aesthetic Emotions (3.31% of Misses)**:
   - **Key Terms**: *breathtaking (1,346), stunning (552), sublime (291), scenic (400), surreal (98), majestic, panoramic, spellbinding, mesmerizing, awe (304)*.
   - *Deep Cause*: Low-altitude air tourism is uniquely defined by **Aerial Visual Awe**, a domain-specific aesthetic emotion completely absent from generic news or conversational lexicons.

4. **Absence of Flight Perceived Risk & Somatic Symptoms (1.84% of Misses)**:
   - **Key Terms**: *claustrophobia, jitters, airsick, phobia, unnerving*.
   - *Deep Cause*: Flight vibration, confined cabin space, and altitude suspense trigger somatic anxiety and perceived risk reactions specific to aviation tourism.
