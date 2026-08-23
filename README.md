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

### 1. Post-Rescued NRC Coverage & Gap Breakdown ($N=630$ Words)

```text
Master Gold Emotion Codebook (N = 630 Words)
│
├── 1️⃣ Post-Rescued NRC Vocabulary Universe ────────────────────────── 485 words (76.98%) ⭐
│   ├── 1a. Directly Mapped to NRC 8-Emotion Categories ───────────── 286 words (45.40%)
│   ├── 1b. Directly Mapped to Positive / Negative Polarity Only ───── 72 words (11.43%)
│   └── 1c. Class 1 Participle & Morphological Rescued Words ─────── 127 words (20.16%) ⭐
│           (via Canonical Lemma Normalization, e.g., loved->love, scared->scare, impressed->impress, safer->safe)
│
└── 2️⃣ Uncovered Domain Gaps (NRC Lexicon Misses) ───────────────────── 145 words (23.02%) ⭐ (CORE FOCUS)
    ├── 2a. Class 2: Web 2.0 Colloquial Superlatives & Base Terms ── 128 words (20.32% | 28,401 mentions)
    │       (e.g., great, awesome, fantastic, nice, incredible, comfortable, fabulous, enjoyable)
            └── Sub-3C: Flight Anxiety (claustrophobic, claustrophobia, jitters, unnerving, phobia)
```

$$	ext{Total NRC Vocabulary Coverage (358)} = 286 	ext{ (8-Emotions)} + 72 	ext{ (Polarity Only)}$$
$$	ext{Total Master Gold Codebook (630)} = 358 	ext{ (Total NRC Covered)} + 272 	ext{ (Completely Missed by NRC)}$$

---

### 2. 3 Core Classes of Generic NRC Lexicon Gaps ($N=272$ Missed Words)

📌 **Class 1: Participle & Morphological Derivation Gaps (127 Words, 46.69%)**:
- **Classification Logic**: Inflected participle forms (-ing, -ed) and adverbs/superlatives (-ly, -est, -er) whose base dictionary roots exist in NRC, but static string matching fails to capture due to lack of morphological derivation rules.
- **Lemma Normalization Rescue**: By applying Canonical Lemma Normalization, all 127 Class 1 morphological variants (e.g., *loved -> love*, *scared -> scare*, *impressed -> impress*, *safer -> safe*) are successfully rescued back into the NRC Covered Universe, expanding total NRC coverage from 358 words (56.83%) to **485 words (76.98%)**.
- **Key Terms**: *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132)*.

📌 **Class 2: Omission of Modern Online Tourism Colloquial Superlatives & Base Terms (128 Words, 47.06%)**:
- **Classification Logic**: High-frequency base terms and colloquial superlatives widely used across Web 2.0 tourism reviews (restaurants, hotels, sights) that are omitted by NRC due to its formal written seed corpus bias (Mohammad & Turney 2012).
- **Unfixable Lexicon Gap**: Unlike Class 1, Class 2 words (e.g., *great, awesome, fantastic*) are base roots themselves and cannot be rescued by lemma normalization. They constitute an unfixable domain gap in traditional NRC lexicons.
- **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.

📌 **Class 3: Low-Altitude Air Tourism Domain-Specific Lexicon (17 Words, 6.25% of Misses | 2,862 Review Mentions)** ⭐ *(CORE PAPER CONTRIBUTION)*:
- **Classification Logic**: Domain-specific somatic symptoms and aesthetic awe terms unique to low-altitude aviation tourism.
- **Sub-Categories**:
  - **Sub-3A: Aerial Visual Awe** ($N=10$ words, 2,791 mentions): *breathtaking, stunning, scenic, awe, surreal, sublime, mesmerizing, awed, breathtakingly, stunningly*.
  - **Sub-3B: Embodied Distress** ($N=1$ word, 33 mentions): *airsick*.
  - **Sub-3C: Situational Flight Anxiety** ($N=6$ words, 38 mentions): *claustrophobic, claustrophobia, jitters, unnerving, phobia, spellbinding*.

- **Official Publication Figures**:
  - 👉 [`fig3_class3_domain_taxonomy.png`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/figures/fig3_class3_domain_taxonomy.png) (Class 3 Domain Taxonomy & Mental State Partition)
  - 👉 [`fig9_sentence_sentiment_vs_rating_scatter.png`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/figures/fig9_sentence_sentiment_vs_rating_scatter.png) (Full Corpus Review-Level Sentiment Density Scatter Plot)
  - 👉 [`fig_exact_word_sentiment_scatter.png`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/figures/fig_exact_word_sentiment_scatter.png) (Word Sentiment Scatter Plot: VADER Score vs Tourist Rating)

---

## 📍 Step 5: Master 508 Sentiment Words & Tourist Experience Objects Codebook

To analyze what specific tourist experience targets cause emotion transitions, we constructed the **Master 508 Sentiment Words & Objects Codebook** (`master_508_sentiment_objects_codebook.xlsx`), mapping all frequency >= 5 gold emotion terms across 5 primary experience targets:

1. **Aerial Scenery & Nature Views** ($N=17$ words): e.g., *breathtaking, stunning, scenic, spectacular, gorgeous, magnificent, awe, sublime, view, glacier, canyon, beautiful*.
2. **Pilot, Crew & Guide Service** ($N=9$ words): e.g., *friendly, pilot, helpful, informative, professional, reassuring, knowledgeable, captain, guide, staff, attentive, kind*.
3. **Flight Riding & Aircraft Feeling** ($N=35$ words): e.g., *smooth, comfortable, exciting, thrill, airsick, claustrophobic, nervous, scared, terrified, turbulence, choppy, fun*.
4. **Booking, Price & Value** ($N=20$ words): e.g., *worth, valuable, reasonable, expensive, delayed, canceled, refund, ruined, disappointing, horrible, terrible, awful*.
5. **Overall Tourism Experience Appraisal** ($N=430$ words): e.g., *great, amazing, best, wonderful, good, awesome, excellent, fantastic, nice, incredible, memorable, happy*.

---

## 📈 Key Empirical Master Artifacts & Directory Map

| Artifact Name | File Format | Record Count | Description & Link | :--- | :---: | :---: | :--- | **Clean Master Dataset** | CSV | 22,235 Rows | Primary master dataset (`tripadvisor_processed_master.csv`) | **Deleted Duplicates Audit** | CSV | 6,683 Rows | Audit log of removed cross-listing duplicates (`deleted_duplicates_audit.csv`) | **Master Gold Emotion Lexicon** | Excel / CSV | 630 Words | Primary domain emotion codebook 👉 [`strict_raw_nrc_630_codebook.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/strict_raw_nrc_630_codebook.xlsx) | **Master 508 Sentiment Objects Codebook** | Excel / CSV | 508 Words | Master sentiment words & experience object mapping 👉 [`master_508_sentiment_objects_codebook.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/master_508_sentiment_objects_codebook.xlsx) | **Plotted 407 VADER Words Dataset** | Excel / CSV | 407 Words | Direct VADER mapped scatter dataset 👉 [`scatter_plot_407_vader_words_dataset.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/scatter_plot_407_vader_words_dataset.xlsx) | **Sentence Emotion Dynamics Summary** | Excel / CSV | 20,727 Rows | Sentence-level valence & arousal dynamics master 👉 [`sentence_emotion_dynamics_summary.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/sentence_emotion_dynamics_summary.xlsx) | **Sentence Sentiment Transitions Master** | Excel / CSV | 20,727 Rows | Fear-to-Awe Peak & Disappointment trajectory master 👉 [`sentence_sentiment_transitions_master.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/sentence_sentiment_transitions_master.xlsx) |

```text
Low-Altitude/
├── article/                              # 📄 Paper Manuscripts & Research Drafts (Preserved)
├── data/                                 # 🧹 Datasets & Derived Lexicon Codebooks
│   ├── cleaned_datasets/                 # Primary master datasets (22,235 clean master)
│   ├── derived_outputs/                  # Master Codebook & Audit Logs (630 Gold vs 8,096 Purged)
│   └── analyze/                          # 7 Locked Master Official Datasets & Excel Tables
├── figures/                              # 📈 Publication-Ready Charts & Maps (Figures 1-13)
│
├── scratch/                              # 💻 8 Clean Production-Grade Python Master Scripts
├── run_data_pipeline.py                  # 🚀 Master Data Pipeline Runner
├── README.md                             # 📄 High-Impact Executive Overview (100% English)
```

## 💻 Quick Reproduction Guide

```bash
# 1. Run full data processing, deduplication, and feature engineering pipeline:
python run_data_pipeline.py

# 2. Run Master 508 Sentiment Words & Objects Codebook Generator:
python scratch/build_master_508_sentiment_objects_codebook.py

# 3. Run Sentence-Level Emotion Dynamics & Russell Circumplex Transition Engine:
python scratch/run_sentence_emotion_dynamics.py
```puts/                  # Master Codebook & Audit Logs (630 Gold vs 8,096 Purged)
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