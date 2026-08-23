# Comprehensive Academic Research Notes & Methodology Log
## Project Title: Low-Altitude Air Tourism NLP Processing, Lexicon Induction & NRC Benchmark Audit

> 🌐 **Repository**: [https://github.com/ypeng12/Low-Altitude](https://github.com/ypeng12/Low-Altitude)  
> 📄 **Main Executive Overview**: [`README.md`](file:///Users/yuliangpeng/Desktop/Low-Altitude/README.md)  
> 🇨🇳 **Chinese Lab Notes**: [`RESEARCH_NOTES_CN.md`](file:///Users/yuliangpeng/Desktop/Low-Altitude/RESEARCH_NOTES_CN.md)

---

## 🌟 Section 1: Research Background & Sample Reconciliation

This document provides exhaustive methodological, algorithmic, and empirical documentation for the **Low-Altitude Air Tourism NLP & Emotion Lexicon Project**.

### 1. Sample Reconciliation Ledger
- **Raw Scraped Universe**: 28,918 observations across 46 air tour products on TripAdvisor.
- **Cross-Listing Deduplication**: TripAdvisor cross-lists reviews across vendor activity pages, creating a **23.1% duplicate rate**. Fingerprint deduplication (`[user_name] + [whitespace_normalized_text]`) removed **6,683 duplicate copies** (`deleted_duplicates_audit.csv`), retaining **22,235 clean master reviews** (`tripadvisor_processed_master.csv`).
- **Corpus Reconciliation**: 21,238 language-detected English reviews $\rightarrow$ **21,215 canonical English reviews** after final text validation ($N=997$ non-English reviews exported separately to `non_english_reviews.csv`).

---

## 🔬 Section 2: Step 2 — Corpus-Derived Master Gold Emotion Lexicon Induction ($N=630$)

Generic off-the-shelf sentiment lexicons (NRC, VADER) fail in specialized experiential domains like Low-Altitude Tourism. To build a domain-specific codebook with rigorous academic transparency, we executed a 3-stage induction methodology across all **21,215 canonical English reviews**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Full Clean English Corpus (N=21,215 Reviews)                               │
└────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                                         │
         ┌───────────────────────────────────────────────┼───────────────────────────────────────────────┐
         ▼                                               ▼                                               ▼
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│ Stage 1: Discovery (N=500 Reviews)   │     │ Stage 2: Expansion (N=2,000)         │     │ Stage 3: Full Completion (N=18,901)  │
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

### 1. Detailed Stage-by-Stage Sampling & Extraction Algorithm

#### 📍 Stage 1: Initial Discovery Induction ($N=500$ Sample)
- **Sampling Protocol**: Stratified random sampling ($N=500$, Seed 42) balanced across 46 air tour products, star rating tiers ($1–5$ stars), aircraft types (helicopters, fixed-wing, floatplanes), and review length quartiles.
- **Extraction & Adjudication**: Tokenized text, removed standard NLTK stop words, and calculated term frequencies. Every unique term was inspected within its original review sentence context (`example_context`).
- **Discoveries**: Identified **372 pure emotion and appraisal terms** (`data/derived_outputs/stage_discovery_500/clean_emotion_words_500_reviews.xlsx`) and 1,855 purged non-emotion terms. Revealed that tourists frequently pair safety reassurance words (*safe*, *smooth*, *reassuring*) with anxiety terms (*nervous*, *scared*, *terrified*), uncovering the core domain mechanism: *Safety Reassurance Mitigates Perceived Fear*.

#### 📍 Stage 2: Gold Expansion & Vocabulary Scaling ($N=2,000$ Sample)
- **Sampling Protocol**: Secondary stratified random sample ($N=2,000$, Seed 100, incorporating 1,814 unique new unsampled reviews).
- **Extraction & Adjudication**: Evaluated candidate terms against Stage 1 vocabulary to uncover novel, lower-frequency emotion terms (*calm*, *pristine*, *exhilarated*).
- **Discoveries**: Added **173 new clean emotion terms** (`data/derived_outputs/stage_gold_2000/clean_emotion_words_2000_reviews.xlsx`). Combined with Stage 1, established a **545-word sample lexicon** out of a 4,513-word candidate universe (545 Gold Words + 3,968 Purged Terms). Formulated explicit purging criteria for social courtesy phrases (*thanks*), geographic entities (*talkeetna*, *maui*), and cognitive stance words (*think*).

#### 📍 Stage 3: Corpus-Wide Completion ($N=18,901$ Unsampled Reviews)
- **Scope**: Scanned all remaining 18,901 unsampled reviews ($21,215 - 2,314 = 18,901$) to eliminate sampling oversight.
- **Extraction Algorithm**: Extracted **4,213 candidate terms** appearing at frequency $\ge 3$. Implemented config-driven JSON classification rules (`stage_final_affect_rules.json`) combined with WordNet POS tag heuristics.
- **Discoveries**: Identified novel high-arousal terms unique to the tail corpus (*calming*, *breathtakingly*, *annoying*, *sublime*, *stressful*, *tranquil*), yielding **63 new clean emotion terms** (`clean_new_emotion_words_18901.xlsx`).

---

### 2. Canonical Lemma Normalization & Adjudication Boundary Rules (`canonical_lemma`)

#### Typo & Morphological Mapping
- **Typo Normalization**: Standardized spelling errors directly to standard dictionary lemmas via `canonical_lemma` (*suprised $\rightarrow$ surprised*, *suprise $\rightarrow$ surprise*, *exhilerating $\rightarrow$ exhilarating*, *aprehensive $\rightarrow$ apprehensive*, *dissapointed $\rightarrow$ disappointed*).
- **Morphological Normalization**: Standardized inflections (*worries $\rightarrow$ worry*, *surprises $\rightarrow$ surprise*, *cherished $\rightarrow$ cherish*, *hates $\rightarrow$ hate*, *dreaded $\rightarrow$ dread*, *scariest $\rightarrow$ scary*).

#### Retained vs. Purged Boundary Rules
- ✅ **Retained (Master Gold Lexicon: 630 Words)**: Experiencer Affective States ($E_1$: *nervous, afraid, scared, relief, thrilled, tranquil, calming, annoying, stressful*), Stimulus Appraisals ($E_2$: *scary, spectacular, smooth, professional, great, amazing, awesome, excellent*), and Aerial Aesthetic Emotions (*breathtakingly, sublime*).
- ❌ **Purged (Master Removed Log: 8,096 Words)**: Physical Entities (*grand, helicopter, glacier, canyon*), Economic Price (*expensive, overpriced*), Procedural Service (*informative, timely*), Interjections (*wow, yay*), and Greetings (*thanks*).

#### Mathematical Partition Completeness
$$\text{Total Screened Universe (8,726)} = \text{Master Gold Lexicon (630)} + \text{Master Removed Log (8,096)}$$
$$\text{Master Gold Lexicon (630)} \cap \text{Master Removed Log (8,096)} = 0 \quad (\text{100% Zero-Overlap Partition})$$

---



---

### 3. Step 2 Exhaustive Retrospective: Human Adjudication & Exclusion Rationale

#### A. Initial State & Problem Statement
Prior to manual adjudication, candidate term extraction from raw tourist reviews yielded 8,726 unique vocabulary terms containing non-emotion words, entity names, courtesy greetings, procedural service ratings, and physical flight sensations. Simple regex or frequency counts produced severe false positives.

#### B. Theoretical & Methodological Debates (What We Discussed & Evaluated)
1. **Experiencer Affect ($E_1$) vs. Stimulus Appraisal ($E_2$)**:
   - We debated whether to include only direct internal emotional states felt by tourists ($E_1$: *nervous, afraid, scared, thrilled, tranquil*) or also subjective evaluations of air tour attributes ($E_2$: *scary, spectacular, smooth, professional, flawless*).
   - *Decision*: Both $E_1$ and $E_2$ were retained as core dimensions of emotion and appraisal in tourism experiences, following established hospitality NLP frameworks.
2. **Purging Boundary Rule 1: Courtesy Greetings & Interjections**:
   - We examined informal interjections (*wow, yay*) and courtesy greetings (*thanks, thank, thankyou*).
   - *Decision*: Purged as social formality greetings and emotive exclamations rather than formal emotion nouns/adjectives.
3. **Purging Boundary Rule 2: Geographic & Physical Entity Names**:
   - Words like *grand* (frequently referring to Grand Canyon), *maui*, *helicopter*, *glacier*, *canyon*, *water*, *blue* were initially extracted due to high frequency.
   - *Decision*: Purged all 8,096 non-emotion physical, spatial, and brand entity terms.
4. **Purging Boundary Rule 3: Monetary Cost & Economic Price Attributes**:
   - Terms like *expensive, overpriced, cheap, price, cost* were evaluated.
   - *Decision*: Purged as economic cost evaluations, shifting them to independent control variables (`price_value_mention`).
5. **Purging Boundary Rule 4: Operational Performance & Procedural Service**:
   - Terms like *informative, timely, seamless, knowledgeable* reflect cognitive stance or objective service efficiency.
   - *Decision*: Purged as operational performance metrics.
6. **Purging Boundary Rule 5: Physical Vibration & Ride Sensation**:
   - Terms like *choppy* (flight turbulence) reflect physical motion sensations rather than internal psychological affect.
   - *Decision*: Purged as physical vibration indicators.

#### C. Manual Adjudication & Calibration Summary
- **Original Candidate Universe**: 8,726 unique terms screened across N=21,215 reviews.
- **Retained Master Gold Emotion Codebook**: **630 Words** (`gold_emotion_lexicon_codebook.xlsx`).
- **Master Purged Non-Emotion Audit Log**: **8,096 Words** (`removed_non_emotion_words_log.xlsx`).
- **Zero-Overlap Partition Check**: $630 	ext{ Gold Words} \cap 8,096 	ext{ Purged Words} = 0$ (100% Zero Overlap).

## 📊 Section 3: Step 3 — Generic Lexicon Audit & 3-Class Failure Gap Taxonomy

In Step 3, we mapped our **630 Master Gold Emotion Terms** (`data/analyze/gold_emotion_master.csv`) against the **NRC Emotion Lexicon v0.92** (14,182 vocabulary entries) using the python audit script [`scratch/audit_gold_630_nrc_tree.py`](file:///Users/yuliangpeng/Desktop/Low-Altitude/scratch/audit_gold_630_nrc_tree.py):

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)
![NRC Missed 3 Classes Chart](figures/nrc_emotion_plots/nrc_missed_3classes_chart.png)

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

$$\text{Total NRC Vocabulary Coverage (358)} = 286 \text{ (8-Emotions)} + 72 \text{ (Polarity Only)}$$
$$\text{Total Master Gold Codebook (630)} = 358 \text{ (Total NRC Covered)} + 272 \text{ (Completely Missed by NRC)}$$

---

### 2. Dual-Layer Matching Protocol: Raw Exact Match vs. Canonical Lemma Match

| Matching Protocol | NRC 8-Emotion Match Count | Only Polarity Count | Completely Missed Count | Total Codebook Universe | Methodological Takeaway |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Raw Exact Match (Unnormalized)** | 269 words (42.70%) | 72 words (11.43%) | 289 words (45.87%) | 630 words | Plurals (-s), past participles (-ed), and typos are lost as "unmapped". |
| **Canonical Lemma Match (Normalized)** | **286 words (45.40%)** | **72 words (11.43%)** | **272 words (43.17%)** | **630 words** | **Rescues 17 true 8-emotion terms via lemma root mapping!** |

---

### 3. Detailed Discovery & Empirical Audit of the 3 Core Miss Classes ($N=272$ Missed Words)

#### 📌 Class 1: Participle & Morphological Derivation Gaps (127 Words, 46.69% | 17,565 Mentions)
- **Discovery Process**: Stripped `-ing, -ed, -ly, -est, -er` suffixes back to dictionary base roots.
- **Empirical Audit Results**: Tested base roots in NRC $\rightarrow$ **48.82% (62 words) have base roots (*amaze, love, impress, inspire, scare, thrill, good, safe*) IN NRC**. However, static string matching fails to capture them, omitting **88.7% (15,581 review mentions)** of emotional expressions.
- **Key Terms**: *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132)*.
- **Methodological Conclusion**: Generic NRC lexicons lack morphological derivation rules, causing massive loss of participle emotion adjectives.

#### 📌 Class 2: Omission of Modern Online Tourism Colloquial Superlatives & Base Terms (128 Words, 47.06% | 28,401 Mentions)
- **Discovery Process**: Filtered non-morphological base words omitted by NRC.
- **Empirical Audit Results**: Programmatically verified that **only 1 exception (`stellar`, 29 mentions) has an NRC tag (`positive`), whereas all remaining 127 base terms are 100% ABSENT from NRC (tags = 0)**.
- **Pareto 80/20 Principle**: **10 top high-frequency colloquial superlatives account for 20,549 mentions (73.2% of Class 2 frequency, and 42.08% of total missed review frequency)** due to formal written seed vocabulary bias in 2012 NRC.
- **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.

#### 📌 Class 3: Low-Altitude Air Tourism Domain-Specific Lexicon (17 Words, 6.25% | 2,862 Mentions)
- **Discovery Process**: Identified unique low-altitude aerial sightseeing emotions completely absent from generic corpora.
- **Sub-dimension A (Aerial Visual Awe, 11 Words, 2,791 Mentions)**:
  - **Key Terms**: *breathtaking (1,346), stunning (552), scenic (400), awe (304), surreal (98), breathtakingly (30), mesmerizing (26), awed (15), sublime (6), spellbinding (4)*.
  - **Empirical Validation**: All 11 awe terms have **0 tags in NRC (100% unmapped)**, omitting **2,791 review mentions**.
  - **Academic Conclusion**: Low-altitude air tourism is uniquely defined by Aerial Visual Awe, a domain-specific aesthetic emotion completely absent from generic news or conversational lexicons.
- **Sub-dimension B (Somatic Flight Risk, 6 Words, 71 Mentions)**:
  - **Key Terms**: *airsick (33), claustrophobic (16), claustrophobia (9), jitters (5), unnerving (4), phobia (4)*.
  - **Empirical Validation**: All 6 flight risk terms have **0 tags in NRC (100% unmapped)**, omitting **71 review mentions**.
  - **Academic Conclusion**: Flight vibration, confined cabin space, and altitude suspense trigger somatic anxiety and perceived risk reactions specific to aviation tourism that generic sentiment dictionaries fail to capture.

---

---

## 💻 Section 5: Technical Implementation Logic & Algorithm Specifications

To ensure publication-grade computational reproducibility, this section documents the exact Python scripts, regex patterns, data structures, and algorithmic logic underlying each pipeline stage.

### 1. Data Cleaning & Fingerprint Deduplication Algorithm (`clean_level1.py`)

#### A. Product Fixed Effect Preservation (`tour_name`)
- **Input**: 46 raw CSV files (e.g., `1-Kauai Deluxe Sightseeing Flight_1623...csv`).
- **Logic**: Simple concatenation loses product identity. We extracted standardized product names via regex:
  ```python
  import re
  tour_name = re.sub(r'^\d+-|_|\d{5,}.*', '', file_path.stem).strip()
  ```
- **Purpose**: Preserves **Product Fixed Effects ($\mu_j$)** in econometric regressions.

#### B. Text Normalization & Fingerprint Deduplication
- **HTML Unescaping & Linebreak Standardization**:
  ```python
  import html
  clean_text = html.unescape(raw_text)
  clean_text = clean_text.replace("<br />", "
").replace("<br/>", "
")
  clean_text = re.sub(r'\s+', ' ', clean_text).strip()
  ```
- **Fingerprint Hash Function**:
  ```python
  import hashlib
  fingerprint = hashlib.md5(f"{user_name.lower().strip()}_{clean_text.lower()}".encode('utf-8')).hexdigest()
  ```
- **Deduplication Audit Results**: Identified 13,116 participating rows in cross-listing duplicate clusters, safely eliminated **6,683 duplicate copies** (`deleted_duplicates_audit.csv`), retaining **22,235 clean master reviews** (`tripadvisor_processed_master.csv`).

---

### 2. Lexicon Induction Pipeline & Code Architecture (`research_modules/emotion_lexicon_induction/`)

#### A. Stratified Sampling Algorithm
- **Stratification Variables**: `rating` (1–5 stars), `tour_name` (46 products), `review_length_quartile` (Q1–Q4).
- **Python Sampling Logic**:
  ```python
  df_sample = df.groupby(['rating', 'review_length_quartile'], group_keys=False).apply(
      lambda x: x.sample(n=min(len(x), target_per_group), random_state=seed)
  )
  ```
- **Random Seeds**: Seed 42 for Stage 1 ($N=500$); Seed 100 for Stage 2 ($N=2,000$).

#### B. Sentence Context Offset Extraction (`example_context`)
- To evaluate candidate terms within exact sentence boundaries rather than isolated tokens:
  ```python
  import nltk
  sentences = nltk.sent_tokenize(review_text)
  for sent in sentences:
      if candidate_word.lower() in sent.lower():
          example_context = sent.strip()
          break
  ```

#### C. Full Corpus Completion Extraction (`build_stage_final_codebook.py`)
- **Candidate Filtering Threshold**: Unsampled corpus ($N=18,901$), term frequency $\ge 3$ (4,213 candidate terms).
- **Rule Engine**: Evaluated via WordNet POS tagging (`nltk.pos_tag`) and JSON classification rules (`stage_final_affect_rules.json`).

---

### 3. Generic Lexicon Audit & Tree Calculation Logic (`scratch/audit_gold_630_nrc_tree.py`)

#### A. NRC Categorization Algorithm
```python
import pandas as pd
from nrclex import NRCLex

df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    # Priority: Try raw word, fallback to canonical_lemma
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    
    if len(set(nrc_tags) & NRC8) > 0:
        category = "1a. NRC 8-Emotion Match"      # 286 words
    elif len(nrc_tags) > 0:
        category = "1b. NRC Polarity Only Match"   # 72 words
    else:
        category = "2. NRC Completely Missed"      # 272 words
```

#### B. Cause 1 Root Stripping Verification Script (`scratch/verify_cause1_lemmas_in_nrc.py`)
- **Logic**: For Cause 1 words ending in `-ing, -ed, -ly, -est, -er`, programmatically strip suffixes to extract candidate base roots and query `NRCLex().__lexicon__`.
- **Result**: Proved **48.82% (62 words) have base roots (*amaze, love, impress, inspire, scare, thrill, good, safe*) IN NRC**, confirming NRC's morphological blindness.

#### C. Cause 2 Pareto 80/20 Script (`scratch/verify_two_percentages.py`)
- **Logic**: Programmatically computed unique word count % ($10/272 = 3.68\%$) vs review mention frequency % ($20,549/48,828 = 42.08\%$).
- **Result**: Proved that top 10 colloquial superlatives (*great, awesome, fantastic, nice, incredible*) dominate 42.08% of total missed review mentions.







##### 🌟 Summary Table of Class 3 Domain Categories

| Domain-Specific Category | Category Description & Theoretical Rationale | Representative Key Terms ($N=17$ Words) |
| :--- | :--- | :--- |
| **Awe** | Aerial Visual Awe & Aesthetic Sublimity (敬畏 / 震撼) | *breathtaking (1,346), stunning (552), scenic (400), awe (304), surreal (98), breathtakingly (30), mesmerizing (26), awed (15), stunningly (10), sublime (6), spellbinding (4)* |
| **Embodied Distress** | Somatic Motion Sickness & Physical Discomfort (身体化不适 / 身体性负面体验) | *airsick (33)* |
| **Situational Anxiety** | Cabin Enclosure & Altitude Perceived Suspense (情境性焦虑) | *claustrophobic (16), claustrophobia (9), jitters (5), unnerving (4), phobia (4)* |

##### 🌟 Comprehensive Breakdown Table of Class 3 Domain Lexicon ($N=17$ Words)

###### Sub-dimension 3A: Awe (敬畏 / 震撼 / 壮美感) [11 Word Variants, 2,791 Mentions]
| Raw Word (`word`) | Root Lemma (`canonical_lemma`) | Corpus Freq ($N=21,215$) | Chinese Translation | Theoretical & Empirical Finding |
| :--- | :--- | :---: | :--- | :--- |
| **`breathtaking`** | **`breathtaking`** | **1,346** | 令人屏息震撼的 | Dominant aerial awe descriptor in glacier/canyon flights. |
| **`stunning`** | **`stunning`** | **552** | 令人目眩震撼的 | High-arousal visual shock from altitude perspective. |
| **`scenic`** | **`scenic`** | **400** | 风景优美的 / 宜人的 | Landscape aesthetic appreciation. |
| **`awe`** | **`awe`** | **304** | 敬畏 / 震撼 | Core aesthetic emotion (Awe / Keltner & Haidt 2003). |
| **`surreal`** | **`surreal`** | **98** | 超现实的 / 梦幻般的 | Dreamlike floating sensation over natural wonders. |
| **`breathtakingly`**| **`breathtakingly`**| **30** | 令人屏息震撼地 | Adverbial intensity modifier of visual awe. |
| **`mesmerizing`** | **`mesmerizing`** | **26** | 令人目眩神迷为之倾倒的 | Hypnotic aesthetic absorption in aerial views. |
| **`awed`** | **`awed`** | **15** | 感到肃然起敬震撼的 | Passive affect state of experiencing aerial awe. |
| **`stunningly`** | **`stunningly`** | **10** | 令人震撼地 | Adverbial visual shock modifier. |
| **`sublime`** | **`sublime`** | **6** | 崇高壮丽绝美的 | Kantian aesthetic sublimity in high-altitude landscape. |
| **`spellbinding`** | **`spellbinding`** | **4** | 扣人心弦迷人的 | Intense captive attention during sightseeing. |

###### Sub-dimension 3B: Embodied Distress (身体化不适 / 身体负性体验) [1 Word Variant in Class 3, 33 Mentions]
| Raw Word (`word`) | Root Lemma (`canonical_lemma`) | Corpus Freq ($N=21,215$) | Chinese Translation | Theoretical & Empirical Finding |
| :--- | :--- | :---: | :--- | :--- |
| **`airsick`** | **`airsick`** | **33** | 晕机的 *(生理躯体反应)* | Somatic motion sickness reaction in small aircraft. |

###### Sub-dimension 3C: Flight Anxiety (飞行焦虑 / 空中不安) [5 Word Variants, 38 Mentions]
| Raw Word (`word`) | Root Lemma (`canonical_lemma`) | Corpus Freq ($N=21,215$) | Chinese Translation | Theoretical & Empirical Finding |
| :--- | :--- | :---: | :--- | :--- |
| **`claustrophobic`**| **`claustrophobic`**| **16** | 感到幽闭恐惧压抑的 | Spatial anxiety in small helicopter/plane cabins. |
| **`claustrophobia`**| **`claustrophobia`**| **9** | 幽闭恐惧症 | Clinical/perceived panic in enclosed flight space. |
| **`jitters`** | **`jitters`** | **5** | 忐忑不安 / 紧张发抖感 | Pre-flight somatic trembling and suspense. |
| **`unnerving`** | **`unnerving`** | **4** | 令人发慌不安吓人的 | Psychological loss of control during flight turbulence. |
| **`phobia`** | **`phobia`** | **4** | 恐惧症 / 恐高心理 | Acrophobia / altitude fear reaction. |

## 📈 Section 4: File Directory & Execution Commands

| Artifact Name | File Path | Operational Purpose |
| :--- | :--- | :--- |
| **Clean Master Dataset** | `data/cleaned_datasets/tripadvisor_processed_master.csv` | Primary master dataset (22,235 clean rows) |
| **Master Gold Codebook** | `data/derived_outputs/gold_emotion_lexicon_codebook.xlsx` | 630 Master Gold Emotion Terms |
| **Master Removed Log** | `data/derived_outputs/removed_non_emotion_words_log.xlsx` | 8,096 Purged Non-Emotion Terms |
| **Audit Script** | `scratch/audit_gold_630_nrc_tree.py` | Executable python audit script for 3-level tree |
| **NRC Missed 3-Classes Chart**| `figures/nrc_emotion_plots/nrc_missed_3classes_chart.png` | Publication-ready academic visualization |

```bash
# Run full data processing pipeline:
python run_data_pipeline.py

# Run NRC audit & tree verification:
python scratch/audit_gold_630_nrc_tree.py
```
