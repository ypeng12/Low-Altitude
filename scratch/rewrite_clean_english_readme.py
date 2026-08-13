#!/usr/bin/env python3
"""Rewrite README.md into a perfectly structured, 100% English 3-Step narrative focusing on Step 2 & Step 3."""

from pathlib import Path

readme_path = Path("README.md")

clean_english_readme = """# Low-Altitude Air Tourism: TripAdvisor Review Processing & Domain-Specific Emotion Lexicon Pipeline

> 🌐 **Project Repository**: [https://github.com/ypeng12/Low-Altitude](https://github.com/ypeng12/Low-Altitude)  
> 📄 **Documentation Matrix**:
> - 🇬🇧 **English Research Notes & Pipeline Overview**: `README.md` (Current File) / `RESEARCH_NOTES.md`
> - 🇨🇳 **Chinese Lab Notes**: `RESEARCH_NOTES_CN.md`

---

## 🌟 Executive Summary & Core Methodological Highlights

This repository provides an end-to-end data engineering and Natural Language Processing (NLP) research pipeline tailored for **Low-Altitude Air Tourism (低空观光旅游)**. Collecting 28,918 raw tourist reviews across **46 low-altitude flight products** (helicopters, fixed-wing aircraft, and floatplanes) on TripAdvisor, this project addresses critical generic lexicon limitations by developing a **Corpus-Derived Master Gold Emotion Lexicon ($N=630$ words)** and conducting a benchmark comparative audit against the **NRC Emotion Lexicon**.

### ✨ 3 Key Methodological Contributions
1. **Step 1 — Publication-Grade Clean Master Sample ($N=22,235$)**: Aggregated 28,918 raw reviews, eliminated a 23.1% cross-listing duplicate rate ($N=6,683$), retaining 22,235 clean master reviews ($N=21,238$ clean English reviews) while preserving **Product Fixed Effects ($\mu_j$)** via `tour_name`.
2. **Step 2 — Corpus-Derived Gold Lexicon Induction ($N=630$ Words)** ⭐ *(Primary Focus)*: Constructed a 630-word domain-specific emotion codebook via a 3-stage sampling methodology ($N=500$ Discovery $\rightarrow$ $N=2,000$ Expansion $\rightarrow$ $N=18,901$ Full Completion), establishing a 100% zero-overlap partition against 8,096 purged non-emotion terms.
3. **Step 3 — Generic Lexicon Failure Audit ($N=272$ Missed Words)** ⭐ *(Primary Focus)*: Empirically audited NRC lexicon coverage gaps, revealing that NRC completely misses 43.17% ($N=272$) of domain emotion vocabulary, categorized into 3 core academic failure classes (Morphological Variants, Web 2.0 Colloquial Superlatives, and Low-Altitude Air Tourism Domain-Specific Lexicon).

---

## 🚀 3-Step Methodological Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Full Clean English Corpus (N=21,215 Reviews)                               │
└────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                                         │
         ┌───────────────────────────────────────────────┼───────────────────────────────────────────────┐
         ▼                                               ▼                                               ▼
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│ STEP 1: Data Cleaning & Deduplication│     │ STEP 2: Gold Lexicon Induction (N=630)│     │ STEP 3: NRC Audit & 3 Miss Classes   │
│ - Scraping 46 Products (28,918 raw)  │     │ - Stage 1 Discovery (N=500: 372 w)   │     │ - NRC Covered: 358 words (56.83%)    │
│ - 6,683 Duplicates Eliminated (23.1%)│     │ - Stage 2 Expansion (N=2k: +173 w)   │     │ - NRC Missed: 272 words (43.17%)     │
│ - 22,235 Master (21,238 English)     │     │ - Stage 3 Completion (N=18.9k: +63 w)│     │ - Class 1: Morphological (46.69%)    │
│ - Product Fixed Effects (tour_name)  │     │ - Canonical Lemma Normalization      │     │ - Class 2: Colloquial (47.06%)       │
│ - Geographic Location Parsing        │     │ - 630 Gold vs 8,096 Purged Log       │     │ - Class 3: Low-Altitude (6.25%)      │
└──────────────────────────────────────┘     └──────────────────────────────────────┘     └──────────────────────────────────────┘
```

---

## 📍 Step 1: Data Scraping, Multi-Level Cleaning & Deduplication ($N=22,235$)

### 1. Scraping & Fixed Effect Preservation (`tour_name`)
- Aggregated raw review CSV files across 46 air tour products on TripAdvisor.
- Extracted clean product names (`tour_name`) to preserve **Product Fixed Effects ($\mu_j$)** in econometric specifications.

### 2. Multi-Level Deduplication Audit
- TripAdvisor cross-lists vendor reviews across multiple activity pages, creating a **23.1% duplicate rate**.
- Formulated fingerprint `[user_name] + [whitespace_normalized_text]`, eliminating **6,683 cross-listing duplicate copies** (`deleted_duplicates_audit.csv`).
- Retained **22,235 clean master reviews** (`tripadvisor_processed_master.csv`).

### 3. Subsetting & Geographic Location Parsing
- **English Sample (`is_english=1`)**: **21,238 reviews (95.52%)** — Primary corpus for NLP models and lexicon induction.
- **Non-English Sample (`is_english=0`)**: **997 reviews (4.48%)** — Exported separately to prevent VADER false zero distortion.
- **Geographic Parsing (`is_us_domestic`)**: Parsed location strings to identify **11,044 US domestic tourists (49.7%)** vs. international tourists.

---

## 📍 Step 2: Corpus-Derived Master Gold Lexicon Induction Pipeline ($N=630$ Words) ⭐ (PRIMARY FOCUS)

Generic sentiment lexicons (NRC, VADER) fail in specialized experiential domains like Low-Altitude Tourism. To build a domain-specific codebook with rigorous academic transparency, we executed a 3-stage induction methodology across all **21,215 clean English reviews**:

### 1. 3-Stage Lexicon Induction Process

#### 🔍 Stage 1: Discovery Induction Sample ($N=500$ Reviews)
- **Protocol**: Stratified random sampling ($N=500$, Seed 42) balanced across rating tiers ($1–5$ stars), 46 air tour products, aircraft types (helicopters, fixed-wing, floatplanes), and review length quartiles.
- **Output**: Extracted **372 clean emotion & appraisal terms** (`data/derived_outputs/stage_discovery_500/clean_emotion_words_500_reviews.xlsx`) and 1,855 purged non-emotion terms.

#### 📈 Stage 2: Gold Expansion Sample ($N=2,000$ Reviews)
- **Protocol**: Secondary stratified random sampling ($N=2,000$, Seed 100, incorporating 1,814 unique new unsampled reviews).
- **Output**: Expanded **173 new clean emotion terms** (`data/derived_outputs/stage_gold_2000/clean_emotion_words_2000_reviews.xlsx`). Combined with Stage 1, established a **545-word sample lexicon** out of 4,513 unique vocabulary terms.

#### 🌐 Stage 3: Full Corpus Completion ($N=18,901$ Unsampled Reviews)
- **Scope**: Scanned all remaining 18,901 unsampled reviews ($21,215 - 2,314 = 18,901$) to eliminate sampling oversight.
- **Output**: Screened 4,213 candidate terms (freq $\ge 3$) to identify **63 new clean emotion terms** (`clean_new_emotion_words_18901.xlsx`).

---

### 2. Canonical Lemma Normalization & Adjudication Rules (`canonical_lemma`)

To prevent typos and inflected forms from fragmenting term frequencies, we instituted **Canonical Lemma Normalization**:
- **Typo Normalization**: `suprised` (4) $\rightarrow$ `surprised`, `suprise` (5) $\rightarrow$ `surprise`, `exhilerating` (7) $\rightarrow$ `exhilarating`, `aprehensive` (3) $\rightarrow$ `apprehensive`, `dissapointed` (8) $\rightarrow$ `disappointed`.
- **Morphological Normalization**: `worries` (38) $\rightarrow$ `worry`, `surprises` (21) $\rightarrow$ `surprise`, `cherished` (8) $\rightarrow$ `cherish`, `hates` (5) $\rightarrow$ `hate`, `dreaded` (4) $\rightarrow$ `dread`, `scariest` $\rightarrow$ `scary`.

#### Retained vs. Purged Boundary Rules
- ✅ **Retained (Master Gold Lexicon: 630 Words)**: Experiencer Affective States ($E_1$: *nervous, afraid, scared, relief, thrilled, tranquil, calming, annoying, stressful*), Stimulus/Service Appraisals ($E_2$: *scary, spectacular, smooth, professional, flawless, great, amazing, awesome, excellent*), and Aerial Aesthetic Emotions (*breathtakingly, sublime*).
- ❌ **Purged (Master Removed Log: 8,096 Words)**: Geographic/Physical Entities (*grand, helicopter, glacier, canyon*), Economic Price (*expensive, overpriced*), Procedural Service (*informative, timely*), Interjections (*wow, yay*), and Greetings (*thanks*).

#### Mathematical Partition Completeness
$$\text{Total Screened Universe (8,726)} = \text{Master Gold Lexicon (630)} + \text{Master Removed Log (8,096)}$$
$$\text{Master Gold Lexicon (630)} \cap \text{Master Removed Log (8,096)} = 0 \quad (\text{100% Zero-Overlap Partition})$$

---

## 📍 Step 3: NRC Benchmark Comparative Audit & 3 Core Classes of Misses ⭐ (PRIMARY FOCUS)

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

$$\text{Total NRC Vocabulary Coverage (358)} = 286 \text{ (8-Emotions)} + 72 \text{ (Polarity Only)}$$
$$\text{Total Master Gold Codebook (630)} = 358 \text{ (Total NRC Covered)} + 272 \text{ (Completely Missed by NRC)}$$

---

### 2. 3 Core Classes of Generic NRC Lexicon Gaps ($N=272$ Missed Words)

All **272 missed words** are systematically classified into 3 core academic failure categories:

#### 📌 Class 1: Participle & Morphological Derivation Gaps (127 Words, 46.69%)
- **Participle Forms (-ing / -ed)** & **Adverbs/Superlatives (-ly, -est, -er)**: e.g., *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132)*.
- **Empirical Validation**: Among the 127 pure morphological words, **48.82% (62 words) have base dictionary roots (e.g., *amaze, love, impress, inspire, scare, thrill, good, safe*) already present in NRC**. However, static string matching fails to capture them, omitting **88.7% (15,581 review mentions)** of high-frequency emotional expressions.
- *Deep Cause & Finding*: Generic NRC lexicons lack morphological derivation rules, causing significant classification omissions.

#### 📌 Class 2: Omission of Modern Online Tourism Colloquial Superlatives & Base Terms (128 Words, 47.06%)
- **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.
- **Empirical Validation**: Even after 100% Lemmatization root mapping, top terms such as `great`, `awesome`, `fantastic`, and `nice` remain 100% ABSENT from NRC. **10 top high-frequency colloquial superlatives account for 20,549 mentions (73.2% of Class 2 frequency, and 42.08% of total missed review frequency)**.
- *Deep Cause & Finding*: NRC 2012 seed vocabulary prioritized formal written English corpora. Modern TripAdvisor reviewers rely heavily on colloquial high-arousal superlatives (*great, awesome, fantastic*), causing widespread generic lexicon failure in Web 2.0 online review contexts.

#### 📌 Class 3: Low-Altitude Air Tourism Domain-Specific Lexicon (17 Words, 6.25%) ⭐ (Domain Specific)
- **Sub-dimension A: Low-Altitude Aerial Visual Awe & Aesthetic Emotions (Domain Awe Gap)**:
  - **Key Terms**: *breathtaking (1,346), stunning (552), scenic (400), awe (304), surreal (98), breathtakingly (30), mesmerizing (26), awed (15), sublime (6), spellbinding (4)*.
  - **Empirical Validation**: All 11 awe terms have **0 tags in NRC (100% unmapped)**, omitting **2,791 review mentions**.
  - **Deep Cause & Finding**: Low-altitude air tourism is uniquely defined by Aerial Visual Awe, a domain-specific aesthetic emotion completely absent from generic news or conversational lexicons.
- **Sub-dimension B: Flight Perceived Risk & Somatic Symptoms (Aviation Risk Gap)**:
  - **Key Terms**: *airsick (33), claustrophobic (16), claustrophobia (9), jitters (5), unnerving (4), phobia (4)*.
  - **Empirical Validation**: All 6 flight risk terms have **0 tags in NRC (100% unmapped)**, omitting **71 review mentions**.
  - **Deep Cause & Finding**: Flight vibration, confined cabin space, and altitude suspense trigger somatic anxiety and perceived risk reactions specific to aviation tourism that generic sentiment dictionaries fail to capture.

---

## 📈 Empirical Metrics Ledger & Artifact Guide

| Empirical Metric / Artifact | Value / File Path | Description & Operational Purpose |
| :--- | :--- | :--- |
| **Total Scraped Raw Reviews** | 28,918 | Initial scraped universe across 46 air tour products |
| **Eliminated Duplicates** | **6,683 (23.1%)** | Cross-listing duplicate removal (`deleted_duplicates_audit.csv`) |
| **Clean Master Dataset** | **22,235** | Primary master dataset (`tripadvisor_processed_master.csv`) |
| **English Sample (`is_english=1`)**| **21,238 (95.52%)** | Primary English NLP corpus |
| **Master Gold Emotion Codebook** | **630 Words** | Primary domain emotion codebook (`gold_emotion_lexicon_codebook.xlsx`) |
| **Master Removed Non-Emotion Log** | **8,096 Words** | Audit log of purged non-emotion terms (`removed_non_emotion_words_log.xlsx`) |
| **NRC Covered Terms** | **358 Words (56.83%)** | NRC mapped codebook subset (`nrc_words_included.xlsx`) |
| **NRC Missed Terms** | **272 Words (43.17%)** | NRC unmapped domain subset (`nrc_words_missed.xlsx`) |

---

## 📁 Repository Structure & Quick Execution Guide

```text
Low-Altitude/
├── data/
│   ├── cleaned_datasets/                 # Processed master datasets
│   │   ├── tripadvisor_processed_master.csv  # Master dataset (22,235 clean rows)
│   │   └── deleted_duplicates_audit.csv      # Audit log of 6,683 removed duplicates
│   └── derived_outputs/                  # Derived N-grams & Codebook Artifacts
│       ├── gold_emotion_lexicon_codebook.xlsx# Master 630 Gold Codebook
│       └── removed_non_emotion_words_log.xlsx# Master 8,096 Purged Log
├── data/analyze/                         # Stage 2 & Stage 3 Audit Scripts & Outputs
│   ├── gold_emotion_master.csv           # 630 Master Gold Codebook input
│   ├── gold_emotion_nrc_combined.xlsx    # Merged 630 Gold words with NRC tags
│   ├── nrc_words_included.xlsx           # 358 NRC covered terms
│   └── nrc_words_missed.xlsx             # 272 NRC missed terms
├── run_data_pipeline.py                  # Master Data Pipeline Runner
├── RESEARCH_NOTES.md                     # Detailed English Research Log
├── RESEARCH_NOTES_CN.md                  # Comprehensive Chinese Lab Notes
└── README.md                             # Main Documentation (This file)
```

```bash
# Execute full pipeline from data cleaning to feature extraction:
python run_data_pipeline.py
```
"""

readme_path.write_text(clean_english_readme, encoding="utf-8")
print("Successfully rewrote README.md into crisp 100% English 3-step narrative!")
