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

Mapping our **630 Master Gold Emotion Terms** (`data/analyze/strict_raw_nrc_630_codebook.csv`) against the **NRC Emotion Lexicon v0.92** (14,182 vocabulary entries) reveals critical generic lexicon coverage gaps across two sequential analytical stages:

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

---

### 1. Stage 1: Static Raw NRC Coverage & 3-Class Miss Baseline ($N=630$ Words)

Under strict static string matching without morphological normalization, NRC covers only 358 words (56.83%), missing **272 words (43.17%)** across 3 distinct gap classes:

```text
Master Gold Emotion Codebook (N = 630 Words)
│
├── 1️⃣ Directly Mapped into NRC Vocabulary Universe ───────────────── 358 words (56.83%)
│   ├── 1a. Directly Mapped to NRC 8-Emotion Categories ───────────── 286 words (45.40%)
│   └── 1b. Directly Mapped to Positive / Negative Polarity Only ───── 72 words (11.43%)
│
└── 2️⃣ Completely MISSED by NRC Lexicon (3 Core Miss Classes) ──── 272 words (43.17%) ⭐ (CORE FOCUS)
    ├── 2a. Class 1: Participle & Morphological Derivation Gaps ─ 127 words (20.16% | 17,565 mentions) ⭐
    │       (e.g., loved, impressed, inspiring, relaxed, scared, amazed, thrilled, better, safer)
    ├── 2b. Class 2: Web 2.0 Colloquial Superlatives & Base Terms ── 128 words (20.32% | 28,401 mentions)
    │       (e.g., great, awesome, fantastic, nice, incredible, comfortable, fabulous, enjoyable)
    └── 2c. Class 3: Low-Altitude Air Tourism Domain Lexicon ─────── 17 words (2.70% | 2,862 mentions) ⭐
            ├── Sub-3A: Aerial Visual Awe (breathtaking, stunning, scenic, awe, surreal, sublime)
            ├── Sub-3B: Embodied Distress (airsick)
            └── Sub-3C: Situational Flight Anxiety (claustrophobic, claustrophobia, jitters, unnerving, phobia)
```

$$\text{Total Raw NRC Vocabulary Coverage (358)} = 286 \text{ (8-Emotions)} + 72 \text{ (Polarity Only)}$$
$$\text{Total Baseline NRC Lexicon Misses (272)} = 127 \text{ (Class 1)} + 128 \text{ (Class 2)} + 17 \text{ (Class 3)}$$

---

### 2. Stage 2: Rescuing Class 1 Morphological Variants into NRC (Lemma Normalization Protocol)

By applying **Canonical Lemma Normalization**, we extract base dictionary roots for all 127 Class 1 inflected terms (*loved -> love*, *scared -> scare*, *impressed -> impress*, *safer -> safe*). Because their base roots exist in NRC, these 127 words are successfully rescued and re-integrated into the NRC Covered Universe:

```text
Post-Rescued Master Gold Emotion Codebook (N = 630 Words)
│
├── 1️⃣ Post-Rescued NRC Vocabulary Universe ────────────────────────── 485 words (76.98%) ⭐
│   ├── 1a. Directly Mapped to NRC 8-Emotion Categories ───────────── 286 words (45.40%)
│   ├── 1b. Directly Mapped to Positive / Negative Polarity Only ───── 72 words (11.43%)
│   └── 1c. Class 1 Morphological Rescued Words ───────────────────── 127 words (20.16%) ⭐
│           (via Canonical Lemma Normalization, e.g., loved->love, scared->scare, impressed->impress, safer->safe)
│
└── 2️⃣ Uncovered Domain Gaps (True NRC Lexicon Misses) ─────────────── 145 words (23.02%) ⭐ (CORE FOCUS)
    ├── 2a. Class 2: Web 2.0 Colloquial Superlatives & Base Terms ── 128 words (20.32% | 28,401 mentions)
    │       (e.g., great, awesome, fantastic, nice, incredible, comfortable, fabulous, enjoyable)
    └── 2b. Class 3: Low-Altitude Air Tourism Domain Lexicon ─────── 17 words (2.70% | 2,862 mentions) ⭐
            ├── Sub-3A: Aerial Visual Awe (breathtaking, stunning, scenic, awe, surreal, sublime)
            ├── Sub-3B: Embodied Distress (airsick)
            └── Sub-3C: Situational Flight Anxiety (claustrophobic, claustrophobia, jitters, unnerving, phobia)
```

$$\text{Post-Rescued NRC Covered Universe (485)} = 358 \text{ (Raw Covered)} + 127 \text{ (Class 1 Rescued)} = \mathbf{485 \text{ Words (76.98\%)}}$$
$$\text{Uncovered Domain Gaps (145)} = 128 \text{ (Class 2 Colloquial)} + 17 \text{ (Class 3 Domain)} = \mathbf{145 \text{ Words (23.02\%)}}$$

---

### 3. Detailed Breakdown of the 3 Core Gap Classes ($N=272$ Missed Words)

📌 **Class 1: Participle & Morphological Derivation Gaps (127 Words, 46.69% of Misses | 17,565 Mentions)** ⭐:
- **Classification Logic**: Inflected participle forms (-ing, -ed) and adverbs/superlatives (-ly, -est, -er) whose base dictionary roots exist in NRC, but static string matching fails to capture due to lack of morphological derivation rules.
- **Rescued Status**: 100% rescued into NRC via Lemma Normalization (*loved -> love [Joy]*, *scared -> scare [Fear]*, *impressed -> impress [Trust]*, *safer -> safe [Trust]*).
- **Key Terms**: *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132)*.

📌 **Class 2: Web 2.0 Tourism Colloquial Superlatives & Base Terms (128 Words, 47.06% of Misses | 28,401 Mentions)**:
- **Classification Logic**: High-frequency base terms and colloquial superlatives widely used across Web 2.0 tourism reviews (restaurants, hotels, sights) that are omitted by NRC due to its formal written seed corpus bias (Mohammad & Turney 2012).
- **Unfixable Lexicon Gap**: Unlike Class 1, Class 2 terms (e.g., *great, awesome, fantastic*) are base roots themselves and cannot be rescued by lemma normalization. They constitute an unfixable domain gap in traditional NRC lexicons.
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

### 4. Multi-Stage Low-Altitude Domain Lexicon Discovery Pipeline ($N=16$ Core Words) ⭐ *(CORE PAPER CONTRIBUTION)*

To extract pure domain-specific emotion and somatic experience expressions unique to low-altitude air tourism, we established a **4-Stage Analytical Discovery Pipeline**:

```text
Full Master Gold Emotion Codebook (N = 620 Words)
│
├── 📍 Stage 1: Unrescued Domain Gap Universe ────────────────────────── 145 words (23.02%)
│              (128 Class 2 Colloquial Terms + 17 Class 3 Domain Terms)
│
├── 📍 Stage 2: VADER Cross-Lexicon Audit ────────────────────────────── 26 words
│              (Filtering out generic words with VADER entries, isolating 26 Dual-Lexicon Misses)
│
├── 📍 Stage 3: Expert Manual Quality & Domain Filter ────────────────── -10 words
│              (Manual removal of 10 general evaluative terms: unforgettable, unique, incredibly, plenty, cheaper, smoother, convenient, handy, forward, reasonable)
│
└── 🏆 Stage 4: Final Core Low-Altitude Domain Discovery Lexicon ──────── 16 words ⭐ (CORE DISCOVERY)
               ├── 👤 1. Self / Somatic Internal Perception (3 words): airsick, claustrophobic, claustrophobia
               │      (Perception Entity: Tourist's own physical body & interior psychological state)
               ├── 🏔️ 2. External Physical Scenery & Environment (8 words): spectacular, scenic, majestic, surreal, sublime, mesmerizing, breathtakingly, stunningly
               │      (Perception Entity: External natural landscape, mountains, canyons, & aerial visual views)
               └── 🧠 3. Cognitive Appraisal & Whole Experience Impact (5 words): awe, awed, incredible, exceptional, phenomenal
                      (Perception Entity: Overall tour experience appraisal & psychological awe impact)
```

$$\mathbf{145 \text{ (Stage 1 Gaps)}} \xrightarrow{\text{VADER Audit}} 26 \text{ (Dual Misses)} \xrightarrow{\text{Expert Manual Filter}} \mathbf{16 \text{ Core Discovery Words}}$$

---

### 📂 Official Saved Dataset Artifacts:
* 👉 **Master 620 Codebook Dataset (Excel)**: [`data/analyze/post_rescued_nrc_620_codebook.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/post_rescued_nrc_620_codebook.xlsx)
* 👉 **Master 620 Codebook Dataset (CSV)**: [`data/analyze/post_rescued_nrc_620_codebook.csv`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/post_rescued_nrc_620_codebook.csv)
* 👉 **Master 16 Perceptual Domain Discovery Lexicon (Excel)**: [`data/analyze/final_16_domain_discovery_words.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/final_16_domain_discovery_words.xlsx)
* 👉 **Master 16 Perceptual Domain Discovery Lexicon (CSV)**: [`data/analyze/final_16_domain_discovery_words.csv`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/final_16_domain_discovery_words.csv)

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


## 📉 扎根理论低分评论（< 3.0 分）归因编码矩阵 (Grounded Theory Low-Rating Matrix, N=295)

在 21,215 篇全量语料中，评价低于 3.0 星的低分评论共 295 篇（占 1.39%）。通过规范的扎根理论三级编码，归纳出 9 大核心主轴低分因素：

| 排名 | 三级选择范畴 (*Selective Category*) | 二级主轴范畴/因素 (*Axial Category*) | 一级开放编码原生典例词 (*Open Code*) | 低分中精确记录频次 (*N*) | 低言占比 (%) |
| :---: | :--- | :--- | :--- | :---: | :---: |
| 1️⃣ | 范畴 1：服务履约失误 | 1.1 天气取消与无法登顶/改签摩擦 | canceled, weather, fog, rain, reschedule | **117 篇** | **39.66%** |
| 2️⃣ | 范畴 1：服务履约失误 | 1.3 地面接驳拉车延误与长时等待 | bus, drive, shuttle, wait, late, delayed | **96 篇** | **32.54%** |
| 3️⃣ | 范畴 2：价格退款摩擦 | 2.1 严苛退款条款与退费纠纷 | refund, money back, deposit, policy | **68 篇** | **23.05%** |
| 4️⃣ | 范畴 1：服务履约失误 | 1.2 航空配重强行分座/拆散伴侣 | seat, weight, split, couple, middle seat | **53 篇** | **17.97%** |
| 5️⃣ | 范畴 2：价格退款摩擦 | 2.2 隐形收费与性价比感知低 | rip off, expensive, waste of money, fee | **43 篇** | **14.58%** |
| 6️⃣ | 范畴 4：人际态度失误 | 4.1 地勤/客服态度冷漠恶劣 | rude, unprofessional, unhelpful, attitude | **38 篇** | **12.88%** |
| 7️⃣ | 范畴 3：体验落差限制 | 3.1 飞行距离太远/看不够近/限制 | far, distance, too high, restricted view | **33 篇** | **11.19%** |
| 8️⃣ | 范畴 3：体验落差限制 | 3.2 严重晕机/身体极度不适 | sick, airsick, nausea, vomit, dizzy | **10 篇** | **3.39%** |
| 9️⃣ | 范畴 4：人际态度失误 | 4.2 飞行员缺乏互动/讲解粗糙 | rushed, quiet pilot, no commentary | **7 篇** | **2.37%** |
