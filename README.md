# Low-Altitude Air Tourism NLP & Emotion Analysis

An end-to-end NLP and econometric research pipeline analyzing **21,215 canonical English TripAdvisor reviews** across **46 helicopter, fixed-wing, and floatplane sightseeing products**.

> 🌐 **Project Repository**: [https://github.com/ypeng12/Low-Altitude](https://github.com/ypeng12/Low-Altitude)  
> 📄 **Detailed Documentation**:
> - 🇬🇧 **Detailed Methodology & Sampling Log**: [`RESEARCH_NOTES.md`](file:///Users/yuliangpeng/Desktop/Low-Altitude/RESEARCH_NOTES.md)
> - 🇨🇳 **Comprehensive Lab Notes**: [`RESEARCH_NOTES_CN.md`](file:///Users/yuliangpeng/Desktop/Low-Altitude/RESEARCH_NOTES_CN.md)

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
│   Rating Misalignment   │    │  Weather, Value & Scenery│    │  272 Missed (43.2%)     │
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

## 📍 Step 2: Corpus-Derived Master Gold Emotion Lexicon ($N=630$ Words)

Generic lexicons fail in low-altitude air tourism. We built a **630-word Master Gold Emotion Codebook** across the **21,215 canonical English reviews**:

### 1. Induction & Adjudication Protocol
- **Multi-Stage Sampling**: $N=500$ Discovery Sample (372 terms) $
ightarrow$ $N=2,000$ Gold Expansion Sample (+173 terms) $
ightarrow$ $N=18,901$ Full Corpus Completion (+63 terms). *(For complete sampling logs, see [`RESEARCH_NOTES.md`](file:///Users/yuliangpeng/Desktop/Low-Altitude/RESEARCH_NOTES.md)).*
- **Canonical Lemma Normalization (`canonical_lemma`)**: Standardized spelling typos (`suprised` $
ightarrow$ `surprised`, `exhilerating` $
ightarrow$ `exhilarating`) and inflections (`worries` $
ightarrow$ `worry`, `surprises` $
ightarrow$ `surprise`).
- **Retained vs. Purged Boundary Rules**:
  - ✅ **Retained (630 Gold Words)**: Experiencer Affective States ($E_1$: *nervous, afraid, scared, relief, thrilled, tranquil, calming, annoying*), Stimulus Appraisals ($E_2$: *scary, spectacular, smooth, professional, great, amazing, awesome*), and Aerial Aesthetic Emotions (*breathtakingly, sublime*).
  - ❌ **Purged (8,096 Purged Log)**: Physical Entities (*grand, helicopter, glacier, canyon*), Price (*expensive, overpriced*), Procedural Service (*informative, timely*), and Interjections (*wow, yay*).
- **Mathematical Partition**: $630 	ext{ Gold Words} \cap 8,096 	ext{ Purged Words} = 0$ (100% Zero-Overlap Guaranteed Partition).

---

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
└── 2️⃣ Completely MISSED by NRC Lexicon (Domain Gaps) ────────────── 272 words (43.17%)
        (e.g., great, amazing, best, awesome, fantastic, incredible, breathtaking, stunning, awe)
```

$$	ext{Total NRC Vocabulary Coverage (358)} = 286 	ext{ (8-Emotions)} + 72 	ext{ (Polarity Only)}$$
$$	ext{Total Master Gold Codebook (630)} = 358 	ext{ (Total NRC Covered)} + 272 	ext{ (Completely Missed by NRC)}$$

---

### 2. 3 Core Classes of Generic NRC Lexicon Gaps ($N=272$ Missed Words)

- **Class 1: Participle & Morphological Derivation Gaps (127 Words, 46.69%)**:
  - *Terms*: *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132)*.
  - *Finding*: 48.82% (62 words) have base dictionary roots in NRC, but static string matching omits **88.7% (15,581 review mentions)** of emotional expressions due to lack of morphological derivation rules.

- **Class 2: Omission of Modern Online Tourism Colloquial Superlatives & Base Terms (128 Words, 47.06%)**:
  - *Terms*: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.
  - *Finding*: 100% absent from NRC even after root lemmatization. **10 top high-frequency colloquial superlatives account for 20,549 mentions (73.2% of Class 2 frequency, and 42.08% of total missed review frequency)** due to formal written seed vocabulary bias.

- **Class 3: Low-Altitude Air Tourism Domain-Specific Lexicon (17 Words, 6.25%)**:
  - *Sub-dimension A (Aerial Visual Awe)*: *breathtaking (1,346), stunning (552), scenic (400), awe (304), surreal (98), breathtakingly (30), mesmerizing (26), awed (15), sublime (6), spellbinding (4)* — 0 tags in NRC (2,791 review mentions omitted).
  - *Sub-dimension B (Somatic Flight Risk)*: *airsick (33), claustrophobic (16), claustrophobia (9), jitters (5), unnerving (4), phobia (4)* — 0 tags in NRC (71 review mentions omitted).

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
├── data/
│   ├── cleaned_datasets/                 # Processed master datasets (22,235 clean master)
│   └── derived_outputs/                  # Master Codebook & Audit Artifacts (630 Gold vs 8,096 Purged)
├── data/analyze/                         # Stage 2 & Stage 3 Audit Scripts & NRC Outputs
├── run_data_pipeline.py                  # Master Data Pipeline Runner
├── RESEARCH_NOTES.md                     # Detailed Sampling Methodology & Research Log
├── RESEARCH_NOTES_CN.md                  # Comprehensive Chinese Research Notes
└── README.md                             # High-Impact Project Overview (This file)
```

---

## 💻 Quick Reproduction Guide

```bash
# Run full data processing, deduplication, and feature engineering pipeline:
python run_data_pipeline.py
```
