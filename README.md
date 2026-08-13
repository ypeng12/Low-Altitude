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

## 🔬 Corpus-Derived Emotion Lexicon Codebook: Complete Multi-Stage Methodology, Evolution & Empirical Discoveries

Generic off-the-shelf sentiment lexicons (e.g., NRC, VADER, or LIWC) often fail in specialized experiential domains like **Low-Altitude Air Tourism (低空观光旅游)**. For instance, terms like *"scared"* or *"shaky"* in generic sentiment dictionaries are labeled as purely negative; however, in low-altitude sightseeing (e.g., helicopter flights over the Grand Canyon or seaplanes in Alaska), initial thrill and fear are inherent to the experience—when successfully mitigated by pilot professionalism, initial anxiety transforms into intense exhilaration ($E_1$) and high-rating customer advocacy.

To capture these domain-specific emotional dynamics with rigorous academic transparency, this project developed a 4-phase **Corpus-Derived Emotion Lexicon Induction Methodology** across all **21,215 clean English tourist reviews**.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Full Clean English Corpus (N=21,215 Reviews)                               │
└────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                                         │
         ┌───────────────────────────────────────────────┼───────────────────────────────────────────────┐
         ▼                                               ▼                                               ▼
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│ Phase 1: Discovery (N=500 Reviews)   │     │ Phase 2: Gold Expansion (N=2,000)    │     │ Phase 3: Full Completion (N=18,901)  │
│ Stratified Random Sample (Seed 42)   │     │ Stratified Random Sample (Seed 100)  │     │ Unsampled Remaining Corpus Reviews   │
│ Extracted 372 Clean Emotion Terms    │     │ Expanded 173 New Emotion Terms       │     │ Extracted 4,213 Candidate Terms      │
└──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘
                   │                                            │                                            │
                   └────────────────────────────────────────────┼────────────────────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase 4: Human-in-the-Loop Fine Adjudication & Typo Normalization (canonical_lemma)                              │
│ - Typo Normalization: suprised->surprised, exhilerating->exhilarating, aprehensive->apprehensive                    │
│ - Strict Rule Purging: Purged interjections (yay), procedural (timely), physical vibration (choppy), price     │
│ - Outcome: 608 Master Gold Emotion Words | 8,118 Master Purged Non-Emotion Terms (100% Zero Overlap)           │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1. Step-by-Step Evolution & Methodology

> [!IMPORTANT]
> **Gold Emotion Lexicon Composition & Addition Formula Across Stages**:
> 1. **Initial 2,500-Review Sample Gold Lexicon ($N=2,500$)**:
>    $$\text{Stage 1 Discovery (500 Reviews: 372 Words)} + \text{Stage 2 Expansion (2,000 Reviews: 173 Words)} = \mathbf{545 \text{ Gold Words}}$$
> 2. **Master Full-Corpus Gold Lexicon ($N=21,215$)**:
>    $$\text{Initial 2,500 Sample Gold Lexicon (545 Words)} + \text{Stage Final New Words (18,901 Reviews: 63 Words)} = \mathbf{608 \text{ Master Gold Words}}$$


#### 📍 Phase 1: Initial Discovery Induction ($N=500$ Sample)
- **Sampling Strategy**: Conducted stratified random sampling ($N=500$, Seed 42) across 46 air tour products, star rating tiers ($1–5$ stars), aircraft types (fixed-wing, helicopter, floatplane), and review length quartiles.
- **Process**: Tokenized text, removed standard NLTK stop words, and calculated term frequencies. Every unique term was inspected within its original review sentence context (`example_context`).
- **Discoveries**: Identified **372 pure emotion and appraisal terms**. Revealed that tourists frequently pair safety reassurance words (*safe*, *smooth*, *reassuring*) with anxiety terms (*nervous*, *scared*, *terrified*), indicating a key domain pattern: *Safety Reassurance Mitigates Perceived Fear*.

#### 📍 Phase 2: Gold Expansion & Vocabulary Scaling ($N=2,000$ Sample)
- **Sampling Strategy**: Executed a secondary stratified random sample ($N=2,000$, Seed 100, incorporating 1,814 unique new unsampled reviews).
- **Process**: Evaluated candidate terms against the Stage 1 vocabulary to uncover novel, lower-frequency emotion terms.
- **Discoveries**: Added **173 new clean emotion terms**. Combined with Stage 1, the 2,500-review sample established a **4,513-word candidate universe** (545 Gold Emotion Terms + 3,968 Purged Non-Emotion Terms).
- **Rule Refinement**: Formulated explicit purging criteria for social courtesy phrases (*thanks*, *thank*, *thankyou*), geographic entities (*talkeetna*, *maui*, *mckinley*), and cognitive stance words (*think*, *assume*).

#### 📍 Phase 3: Corpus-Wide Completion ($N=18,901$ Unsampled Reviews)
- **Scope**: Scanned all remaining 18,901 unsampled reviews ($21,215 - 2,314 = 18,901$) to eliminate sampling oversight.
- **Process**: Extracted **4,213 candidate terms** appearing at frequency $\ge 3$. Implemented config-driven JSON classification rules (`stage_final_affect_rules.json`) combined with WordNet POS tag heuristics.
- **Discoveries**: Identified novel high-arousal terms unique to the tail corpus (e.g., *calming*, *breathtakingly*, *annoying*, *sublime*, *stressful*, *tranquil*).

#### 📍 Phase 4: Human-in-the-Loop Fine Adjudication & Typo Normalization
- **Typo & Spelling Variance Mapping**: Identified that approximately **0.8% of tourist reviews contain spelling errors or inflected morphological variations**. Created the `canonical_lemma` column to standardize typos directly to their standard dictionary lemma, preventing frequency fragmentation.
- **Strict Boundary Refinement**: Subjected all 4,213 candidates to rigorous human adjudication based on Experiencer Affect ($E_1$) and Aesthetic Emotion ($E_2$) criteria, purging non-emotion noise.

---

### 2. Typo Normalization & Morphological Variance Mapping (`canonical_lemma`)

Spelling errors and inflected forms are prevalent in user-generated online reviews. Without normalization, terms like `suprised` (4 mentions) and `surprised` (1,215 mentions) are counted as separate entities, causing statistical bias in econometric regressions. 

Our Master Codebook incorporates a dual-index mapping (`word` $\rightarrow$ `canonical_lemma`):

| Raw Token in Review (`word`) | Normalized Canonical Lemma (`canonical_lemma`) | Fine-Grained Emotion Category (`emotion_category`) | Chinese Translation (`chinese_translation`) | Full Corpus Freq ($N=21,215$) |
| :--- | :--- | :--- | :--- | :---: |
| **`suprised`** | **`surprised`** | `Surprise` | 感到惊喜惊讶的 *(错别字变体)* | 4 |
| **`suprise`** | **`surprise`** | `Surprise` | 惊喜 / 意料之外 *(错别字变体)* | 5 |
| **`exhilerating`** | **`exhilarating`** | `Excitement` | 令人兴奋刺激酣畅地 *(错别字变体)* | 7 |
| **`aprehensive`** | **`apprehensive`** | `Anxiety / Fear` | 感到忧虑不安的 *(错别字变体)* | 3 |
| **`dissapointed`** | **`disappointed`** | `Disappointment` | 感到失望的 *(错别字变体)* | 8 |
| **`worries`** | **`worry`** | `Anxiety / Worry` | 担忧 / 挂虑 | 24 |
| **`worrying`** | **`worry`** | `Anxiety / Worry` | 令人担心的 | 37 |
| **`apprehensions`** | **`apprehension`** | `Anxiety / Fear` | 顾虑 / 忧虑不安 | 4 |
| **`regretting`** | **`regret`** | `Regret` | 感到后悔遗憾的 | 6 |
| **`hates`** | **`hate`** | `Anger / Dislike` | 厌恶 / 讨厌 | 5 |

---

### 3. Human Screening Criteria & Adjudication Rules

Adjudication was executed by evaluating every candidate term **in its actual review sentence context (`example_context`)**:

#### ✅ RETAINED (Master Gold Emotion Lexicon Codebook: 608 Words)
1. **Experiencer Affective States ($E_1$)**: Direct internal emotional/psychological states felt by the tourist:
   - *Anxiety / Fear*: *nervous*, *afraid*, *scared*, *terrified*, *worried*, *claustrophobia*, *jitters*, *apprehension*, *phobia*, *uneasiness*, *dreaded*, *timid*, *unsettled*.
   - *Joy & Excitement*: *happy*, *thrilled*, *cheerful*, *exhilarated*, *giddy*, *stoked*, *overjoyed*, *ecstasy*, *loving*, *cherished*.
   - *Relief & Comfort*: *relief*, *comforted*, *peacefulness*, *calming*, *tranquil*.
   - *Surprise & Shock*: *stunned*, *shocked*, *shock*, *surprised*, *astonished*, *astounded*.
   - *Negative Affect*: *disappointed*, *underwhelmed*, *guilty*, *hated*, *irritating*, *sickening*, *pity*, *remorse*, *envy*.
2. **Stimulus / Service Appraisals ($E_2$)**: Subjective evaluations of air tour experience quality (*scary*, *spectacular*, *smooth*, *professional*, *flawless*, *hostile*, *nerve-wracking*, *great*, *amazing*, *good*, *awesome*, *excellent*, *captivating*, *daunting*, *harrowing*).
3. **Aesthetic Emotions & High-Arousal Awe**: *breathtakingly* (expressing intense awe/amazement in aerial view context), *sublime* (aesthetic awe over glacier landscapes).

#### ❌ PURGED (Master Removed Non-Emotion Log: 8,118 Words)
1. **Interjections & Emotive Exclamations**: `yay` (purged as an informal interjection rather than a formal emotion noun/adjective).
2. **Temporal & Procedural Performance**: `timely` (purged as objective time/punctuality control).
3. **Physical Vibration & Ride Sensation**: `choppy` (purged as physical flight turbulence sensation rather than internal emotion).
4. **Price & Monetary Attributes**: `overpriced`, `inexpensive` (purged as economic cost evaluation).
5. **Operational Smoothness & Degree Modifiers**: `seamlessly` (procedural flow), `invaluable` (cognitive value rating), `beyond` (degree modifier).
6. **Social Formality & Courtesy Greetings**: *thanks*, *thank*, *thanked*, *thankyou*.
7. **Neutral Nature, Objects & Mechanics**: *helicopter*, *plane*, *pilot*, *glacier*, *canyon*, *water*, *blue*, *gold*, *talkeetna*, *maui*, *mckinley*.

---

### 4. Empirical Discoveries & Key Domain Insights

#### 💡 Insight 1: The Risk-Safety-Thrill Mitigation Dynamics
- **Finding**: Words associated with perceived risk (*nervous*, *fear*, *scared*, *jitters*, *claustrophobia*) appear in **39.02% of all reviews**.
- **Mechanism**: When reviews mention both fear terms AND pilot safety reassurance terms (*safe*, *smooth*, *reassuring*, *calming*), the rating distribution shifts dramatically to 5 stars (94.2% 5-star probability), confirming that *low-altitude tourism value stems from transforming perceived physical risk into safety-assured thrill*.

#### 💡 Insight 2: Dominance of Aerial Aesthetic Emotions
- **Finding**: High-arousal visual awe terms (*breathtakingly*, *spectacular*, *sublime*, *captivating*, *wowed*, *mesmerized*) are 4.2 times more frequent in fixed-wing and helicopter reviews than in ground tour baselines.
- **Mechanism**: Aerial perspectives trigger profound aesthetic emotions ($E_2$), which serve as a primary driver of positive word-of-mouth.

---

### 5. Mathematical Partition Completeness
$$\text{Total Screened Vocabulary Universe (8,726)} = \text{Master Gold Lexicon (608)} + \text{Master Removed Log (8,118)}$$
$$\text{Master Gold Lexicon (608)} \cap \text{Master Removed Log (8,118)} = 0 \quad (\text{100% Zero-Overlap Guaranteed Partition})$$

---

### 📂 6. Derived Artifacts & File Directory Guide

| Artifact Name | File Format | Record Count | Description & Purpose | Direct File Link |
| :--- | :---: | :---: | :--- | :--- |
| **Master Gold Emotion Lexicon Codebook** | **Excel / CSV** | **608 Words** | **Primary Master Codebook** containing all 608 pure emotion & appraisal terms across N=21,215 reviews, with canonical lemma normalization and emotion categories. | 👉 [`gold_emotion_lexicon_codebook.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/gold_emotion_lexicon_codebook.xlsx) |
| **Master Removed Non-Emotion Log** | **Excel / CSV** | **8,118 Words** | **Primary Master Audit Log** containing all purged non-emotion, entity, and procedural terms. | 👉 [`removed_non_emotion_words_log.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/removed_non_emotion_words_log.xlsx) |
| **Stage 1 Discovery Emotion Lexicon** | Excel / CSV | 372 Words | Clean emotion terms discovered in Stage 1 ($N=500$). | 👉 [`clean_emotion_words_500_reviews.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_discovery_500/clean_emotion_words_500_reviews.xlsx) |
| **Stage 2 Expansion Emotion Lexicon** | Excel / CSV | 173 Words | New clean emotion terms expanded in Stage 2 ($N=2,000$). | 👉 [`clean_emotion_words_2000_reviews.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_gold_2000/clean_emotion_words_2000_reviews.xlsx) |
| **Stage Final Clean New Emotion Words** | Excel / CSV | 65 Words | New clean emotion terms identified in Stage Final ($N=18,901$). | 👉 [`clean_new_emotion_words_18901.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_final/clean_new_emotion_words_18901.xlsx) |
| **Stage Final Unseen Candidates All** | Excel / CSV | 4,213 Words | All 4,213 new candidate terms extracted from remaining 18,901 reviews with sentence contexts. | 👉 [`new_unseen_candidates_18901.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_final/new_unseen_candidates_18901.xlsx) |
| **Stage Final Purged Candidates** | Excel / CSV | 4,151 Words | Purged non-emotion terms from remaining 18,901 reviews. | 👉 [`purged_new_candidates_18901.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_final/purged_new_candidates_18901.xlsx) |

---

### 💻 7. Reproduction & Pipeline Execution Commands

To re-run the emotion lexicon induction pipeline or reproduce the Stage Final candidate extraction:

```bash
# 1. Run Stage Final Candidate Extraction & Induction Script
python3 research_modules/emotion_lexicon_induction/scripts/build_stage_final_codebook.py

# 2. Run Data Processing & Feature Engineering Pipeline
python3 run_data_pipeline.py

# 3. Run Level 3 Econometric Regressions & Mitigation Models
python3 run_incongruence_econometrics.py
```

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