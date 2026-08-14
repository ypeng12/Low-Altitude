# Low-Altitude Air Tourism NLP & Emotion Analysis

An end-to-end NLP and econometric research pipeline analyzing **21,215 canonical English TripAdvisor reviews** across **46 helicopter, fixed-wing, and floatplane sightseeing products**.

> 🌐 **Project Repository**: [https://github.com/ypeng12/Low-Altitude](https://github.com/ypeng12/Low-Altitude)  

---

## 🌟 Key Research Contributions

- **Cleaned & Deduplicated Corpus**: Filtered 28,918 raw reviews down to **22,235 deduplicated master reviews** ($N=21,238$ language-detected English reviews $
ightarrow$ **21,215 canonical English reviews** after final validation).
- **Corpus-Derived Gold Emotion Lexicon ($N=630$)**: Constructed a 630-word human-adjudicated domain emotion codebook via multi-stage sampling, achieving a 100% zero-overlap partition against **8,096 purged non-emotion terms**.
- **Generic Lexicon Failure & NRC Benchmark Audit**: Benchmarked against NRC v0.92, revealing that generic lexicons completely miss **43.17% ($N=272$)** of domain emotion terms across 3 core failure classes (Morphological Variants, Web 2.0 Colloquial Superlatives, and Low-Altitude Domain-Specific Lexicon).
- **Emotion-Rating Incongruence & Feature Engineering**: Engineered **11 domain-specific binary indicators**, VADER sentiment scores, geographic tourist origins, and touchpoint features to analyze emotion-rating mismatch.

---

## 🚀 High-Level Pipeline Architecture

```
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│       Raw Reviews       │    │  Step 1: Deduplication  │    │ Step 2: Gold Lexicon    │
│  46 Air Tour Products   │───►│ Fingerprint Cleaning    │───►│ Human-Adjudicated Code  │
│    (28,918 Raw Rows)    │    │  (22,235 Clean Master)  │    │    (630 Gold Words)     │
└─────────────────────────┘    └─────────────────────────┘    └────────────┬────────────┘
                                                                           │
                                                                           ▼
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│ Econometric Modeling    │    │ 11 Binary Indicators    │    │ Step 3: NRC Benchmark   │
│ Emotion Incongruence &  │◄───│  Touchpoints, Safety,   │◄───│  358 Covered (56.8%)    │
│   Rating Misalignment   │    │  Weather, Value & Scenery│    │  272 Domain Gaps (43.2%)     │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
```

---

## 📍 Step 1: Data Cleaning, Deduplication & Quality Control

### 1. Sample Reconciliation & Number Consistency
- **Raw Universe**: 28,918 observations scraped across 46 air tour products.
- **Cross-Listing Deduplication**: TripAdvisor cross-lists reviews across vendor pages (23.1% duplicate rate). Fingerprint deduplication removed **6,683 duplicate copies** (`deleted_duplicates_audit.csv`), retaining **22,235 clean master reviews**.
- **Corpus Reconciliation**: 21,238 language-detected English reviews $
ightarrow$ **21,215 canonical English reviews** after final text validation ($N=997$ non-English reviews exported separately to `non_english_reviews.csv`).

### 2. Feature Engineering (11 Domain Binary Indicators)
Extracted domain-specific binary indicators using regular expression matching:
- **Service Touchpoints**: `pilot_mention` (61.74%), `guide_mention` (8.77%), `staff_service_mention` (15.77%).
- **Perceived Risk & Value**: `safety_mention` (39.02%), `price_value_mention` (43.85%).
- **Context & Equipment**: `weather_mention` (22.28%), `canyon_mention` (15.12%), `special_occasion` (13.11%), `helicopter_comparison` (12.25%), `coast_mention` (8.90%), `waterfall_mention` (5.39%).

---

## 📍 Step 2: Corpus-Derived Master Gold Emotion Lexicon ($N=630$ Words) ⭐ (PRIMARY FOCUS)

Generic sentiment lexicons (NRC, VADER) fail in specialized experiential domains like Low-Altitude Tourism. To build a domain-specific codebook with rigorous academic transparency, we executed a 3-stage induction methodology across all **21,215 clean English reviews**:

### 1. Step-by-Step Multi-Stage Lexicon Induction Process

#### 📍 Stage 1: Discovery Induction Sample ($N=500$ Reviews)
- **Sampling Protocol**: Stratified random sampling ($N=500$, Seed 42) balanced across rating tiers ($1–5$ stars), 46 air tour products, aircraft types (helicopters, fixed-wing, floatplanes), and review length quartiles.
- **Process & Discoveries**: Evaluated candidates in sentence context (`example_context`). Extracted **372 clean emotion terms** and 1,855 purged non-emotion terms. Uncovered the co-occurrence mechanism between fear/anxiety terms (*nervous, afraid, scared*) and safety reassurance terms (*safe, smooth, reassuring*).
- **Artifact File**: 👉 [`clean_emotion_words_500_reviews.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_discovery_500/clean_emotion_words_500_reviews.xlsx) (372 Words).

#### 📍 Stage 2: Gold Candidate Expansion Sample ($N=2,000$ Reviews)
- **Sampling Protocol**: Secondary stratified random sampling ($N=2,000$, Seed 100, incorporating 1,814 unique new unsampled reviews).
- **Process & Discoveries**: Screened candidates against Stage 1 vocabulary to uncover lower-frequency emotion terms (*pristine, calm, exhilarated*). Formulated strict purging rules to eliminate courtesy greetings (*thanks*), geographic entities (*talkeetna, maui*), and cognitive stance verbs (*think*). Added **173 new clean emotion terms** (545 cumulative sample gold words out of 4,513 candidate terms).
- **Artifact File**: 👉 [`clean_emotion_words_2000_reviews.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_gold_2000/clean_emotion_words_2000_reviews.xlsx) (+173 Words).

#### 📍 Stage 3: Full Corpus Completion ($N=18,901$ Unsampled Reviews)
- **Sampling Protocol**: Scanned all remaining 18,901 unsampled reviews ($21,215 - 2,314 = 18,901$) to eliminate sampling oversight.
- **Process & Discoveries**: Filtered 4,213 candidate terms (frequency $\ge 3$) using automated WordNet POS tagging heuristics and JSON rule engine (`stage_final_affect_rules.json`). Identified **63 new clean emotion terms** unique to the tail corpus (*calming, breathtakingly, annoying, sublime, stressful, tranquil*).
- **Artifact Files**: 👉 [`clean_new_emotion_words_18901.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_final/clean_new_emotion_words_18901.xlsx) (+63 Words) & [`purged_new_candidates_18901.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/stage_final/purged_new_candidates_18901.xlsx) (4,150 Purged Terms).

#### 📍 Codebook Synthesis & Normalization Protocol (`canonical_lemma`)
- **Combined Synthesis**: $372 \text{ (Stage 1)} + 173 \text{ (Stage 2)} + 63 \text{ (Stage 3)} = 608 \text{ pure emotion words}$ + 22 fine-grained calibration adjustments $\rightarrow$ **630 Master Gold Emotion Words** vs **8,096 Master Purged Non-Emotion Terms**.
- **Canonical Lemma Normalization**: Standardized spelling typos (`suprised` $\rightarrow$ `surprised`, `exhilerating` $\rightarrow$ `exhilarating`) and inflections (`worries` $\rightarrow$ `worry`, `surprises` $\rightarrow$ `surprise`, `cherished` $\rightarrow$ `cherish`).
- **Mathematical Partition Completeness**: $630 \text{ Gold Words} \cap 8,096 \text{ Purged Words} = 0$ (100% Zero-Overlap Guaranteed Partition).
- **Master Artifacts**: 👉 [`gold_emotion_lexicon_codebook.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/gold_emotion_lexicon_codebook.xlsx) (630 Gold Words) & [`removed_non_emotion_words_log.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/removed_non_emotion_words_log.xlsx) (8,096 Purged Log).

## 📍 Step 3: NRC Benchmark Comparative Audit & 3 Core Classes of Misses

Mapping our **630 Master Gold Emotion Terms** (`data/analyze/gold_emotion_master.csv`) against the **NRC Emotion Lexicon v0.92** (14,182 vocabulary entries) reveals critical generic lexicon coverage gaps:

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

### 1. 3-Level NRC Coverage Breakdown ($N=630$ Words)

```text
Master Gold Emotion Codebook (N = 630 Words)
│
├── 1️⃣ Total Mapped into NRC Vocabulary Universe ───────────────── 358 words (56.83%)
│   ├── 1a. Mapped to NRC 8-Emotion Categories ────────────────── 286 words (45.40%)
│   │       (via Canonical Lemma Normalization, rescuing 17 inflected/typo words)
│   └── 1b. Mapped to Positive / Negative Polarity Only ──────── 72 words (11.43%)
│           (e.g., worth, interesting, cool, calm, fortunate, grateful, pristine)
│
└── 2️⃣ Completely MISSED by NRC Lexicon (3 Core Miss Classes) ──── 272 words (43.17%) ⭐ (CORE FOCUS)
    ├── 2a. Class 1: Participle & Morphological Derivation Gaps ─ 127 words (46.69% of misses | 17,565 mentions)
    │       (e.g., loved, impressed, inspiring, relaxed, scared, amazed, thrilled, better, safer)
    ├── 2b. Class 2: Colloquial Superlatives & Base Terms ─────── 128 words (47.06% of misses | 28,401 mentions)
    │       (e.g., great, awesome, fantastic, nice, incredible, comfortable, fabulous, enjoyable)
    └── 2c. Class 3: Low-Altitude Air Tourism Domain Lexicon ──── 17 words (6.25% of misses | 2,862 mentions) ⭐
            ├── Sub-A: Aerial Visual Awe (breathtaking, stunning, scenic, awe, surreal, sublime)
            └── Sub-B: Flight Perceived Risk & Somatic Symptoms (airsick, claustrophobic, jitters, phobia)
```

$$	ext{Total NRC Vocabulary Coverage (358)} = 286 	ext{ (8-Emotions)} + 72 	ext{ (Polarity Only)}$$
$$	ext{Total Master Gold Codebook (630)} = 358 	ext{ (Total NRC Covered)} + 272 	ext{ (Completely Missed by NRC)}$$

---

### 2. 3 Core Classes of Generic NRC Lexicon Gaps ($N=272$ Missed Words)

📌 **Class 1: Participle & Morphological Derivation Gaps (127 Words, 46.69%)**:
- **Key Terms**: *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132)*.
- **Empirical Finding**: 48.82% (62 words) have base dictionary roots in NRC, but static string matching omits **88.7% (15,581 review mentions)** of emotional expressions due to lack of morphological derivation rules.

📌 **Class 2: Omission of Modern Online Tourism Colloquial Superlatives & Base Terms (128 Words, 47.06%)**:
- **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.
- **Empirical Finding**: 100% absent from NRC even after root lemmatization. **10 top high-frequency colloquial superlatives account for 20,549 mentions (73.2% of Class 2 frequency, and 42.08% of total missed review frequency)** due to formal written seed vocabulary bias in 2012 NRC.

📌 **Class 3: Low-Altitude Air Tourism Domain-Specific Lexicon (17 Words, 6.25% of Misses | 2,862 Review Mentions)** ⭐ *(CORE PAPER CONTRIBUTION)*:
- **Sub-dimension A: Low-Altitude Aerial Visual Awe & Aesthetic Emotions (11 Words, 2,791 Mentions)**:
  - *Key Terms*: **`breathtaking`** (1,346), **`stunning`** (552), **`scenic`** (400), **`awe`** (304), **`surreal`** (98), **`breathtakingly`** (30), **`mesmerizing`** (26), **`awed`** (15), **`stunningly`** (10), **`sublime`** (6), **`spellbinding`** (4).
  - *Finding*: 100% UNMAPPED in NRC (0 emotion/polarity tags). Low-altitude flight creates high-arousal visual awe over canyons and glaciers, an aesthetic emotion dimension completely absent from generic written lexicons.
- **Sub-dimension B: Flight Perceived Risk & Somatic Symptoms (6 Words, 71 Mentions)**:
  - *Key Terms*: **`airsick`** (33), **`claustrophobic`** (16), **`claustrophobia`** (9), **`jitters`** (5), **`unnerving`** (4), **`phobia`** (4).
  - *Finding*: 100% UNMAPPED in NRC (0 emotion/polarity tags). Flight vibration, confined cabin space, and altitude suspense trigger somatic anxiety reactions unique to aviation tourism.

---

## 📈 Key Empirical Artifacts & Directory Map

| Artifact Name | File Format | Record Count | Description & Link |
| :--- | :---: | :---: | :--- |
| **Clean Master Dataset** | CSV | 22,235 Rows | Primary master dataset (`tripadvisor_processed_master.csv`) |
| **Deleted Duplicates Audit** | CSV | 6,683 Rows | Audit log of removed cross-listing duplicates (`deleted_duplicates_audit.csv`) |
| **Master Gold Emotion Lexicon** | Excel / CSV | 630 Words | Primary domain emotion codebook 👉 [`gold_emotion_lexicon_codebook.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/gold_emotion_lexicon_codebook.xlsx) |
| **Master Removed Non-Emotion Log**| Excel / CSV | 8,096 Words | Primary audit log of purged non-emotion terms 👉 [`removed_non_emotion_words_log.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/removed_non_emotion_words_log.xlsx) |
| **NRC Covered Terms Table** | Excel / CSV | 358 Words | NRC mapped codebook subset 👉 [`nrc_words_included.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/nrc_words_included.xlsx) |
| **NRC Missed Terms Table** | Excel / CSV | 272 Words | NRC unmapped domain subset 👉 [`nrc_words_missed.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/nrc_words_missed.xlsx) |

```text
Low-Altitude/
├── article/                              # 📄 Paper Manuscripts & Research Drafts (Preserved)
├── data/                                 # 🧹 Datasets & Derived Lexicon Codebooks
│   ├── cleaned_datasets/                 # Primary master datasets (22,235 clean master)
│   ├── derived_outputs/                  # Master Codebook & Audit Logs (630 Gold vs 8,096 Purged)
│   └── analyze/                          # NRC Audit Combined Outputs & Excel Tables
├── figures/                              # 📈 Publication-Ready Charts & Maps
│
├── scripts/                              # 💻 Clean Categorized Python Scripts
│   ├── data_cleaning/                    # Phase 1: Deduplication, HTML cleaning & feature indicators
│   ├── lexicon_induction/                # Phase 2: 500 -> 2,000 -> 18,901 multi-stage codebook induction
│   ├── nrc_audit/                        # Phase 3: NRC 3-level tree audit & 3 core miss classes
│   ├── visualization/                    # Publication-grade academic plot generators
│   └── econometrics/                     # Econometric regression models & rating mismatch
│
├── run_data_pipeline.py                  # 🚀 Master Data Pipeline Runner
├── README.md                             # 📄 High-Impact Executive Overview (100% English)
```

## 💻 Quick Reproduction Guide

```bash
# Run full data processing, deduplication, and feature engineering pipeline:
python run_data_pipeline.py
```
