#!/usr/bin/env python3
"""Update README.md with comprehensive multi-stage emotion induction methodology documentation."""

from pathlib import Path

readme_path = Path("README.md")

new_section = """## 🔬 Corpus-Derived Emotion Lexicon Codebook & Multi-Stage Induction Methodology

To avoid relying blindly on fixed generic sentiment lexicons (e.g., NRC or VADER), this project implements a 3-stage **Corpus-Derived Emotion Lexicon Induction Methodology** tailored specifically for low-altitude air tourism. Across all **21,215 clean English reviews**, we extract, normalize, and human-adjudicate domain-specific emotion and appraisal terms.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Full English Corpus (N=21,215 Reviews)                                 │
└────────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                     │
         ┌───────────────────────────────────────────┼───────────────────────────────────────────┐
         ▼                                           ▼                                           ▼
┌────────────────────────────────┐       ┌────────────────────────────────┐       ┌────────────────────────────────┐
│  Stage 1: Discovery (N=500)    │       │ Stage 2: Gold Expansion (N=2k) │       │ Stage Final: Full (N=18,901)   │
│  Stratified Sample (Seed 42)   │       │ Stratified Sample (Seed 100)   │       │ Unsampled Remaining Reviews    │
│  372 Emotion Terms Extracted   │       │ 173 New Emotion Terms Added    │       │ 65 New Emotion Terms Added     │
└───────────────┬────────────────┘       └───────────────┬────────────────┘       └───────────────┬────────────────┘
                │                                        │                                        │
                └────────────────────────────────────────┼────────────────────────────────────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            Master Gold Emotion Lexicon Codebook (N=21,215)                              │
│                608 Pure Emotion Words | Typo Normalization (canonical_lemma) | 8,118 Purged Log         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1. Multi-Stage Sampling & Induction Pipeline

#### 📍 Stage 1: Discovery Sample ($N=500$ Reviews)
- **Sampling Protocol**: Stratified random sampling ($N=500$, Seed 42) balanced across rating distributions, 46 air tour products, aircraft types, and review length bins.
- **Induction Output**: Extracted **372 clean emotion terms** (`data/derived_outputs/stage_discovery_500/clean_emotion_words_500_reviews.xlsx`) and **1,855 purged non-emotion terms**.

#### 📍 Stage 2: Gold Candidate Expansion Sample ($N=2,000$ Reviews)
- **Sampling Protocol**: Stratified random sampling ($N=2,000$, Seed 100, comprising 1,814 unique new unsampled reviews).
- **Induction Output**: Extracted **173 new clean emotion terms** (`data/derived_outputs/stage_gold_2000/clean_emotion_words_2000_reviews.xlsx`) and **2,113 purged terms**.
- **Combined 2,500 Sample Universe**: Yielded **545 Gold Emotion Words** and **3,968 Purged Terms** ($N=4,513$ unique vocabulary terms).

#### 📍 Stage Final: Full Corpus Completion ($N=18,901$ Remaining Reviews)
- **Sampling Protocol**: All remaining unsampled reviews ($21,215 - 2,314 = 18,901$ reviews).
- **Induction Output**: Extracted **4,213 candidate terms** (frequency $\\ge 3$). Screened and human-adjudicated to identify **65 new emotion terms** (`data/derived_outputs/stage_final/clean_new_emotion_words_18901.xlsx`) and **4,151 purged terms** (`data/derived_outputs/stage_final/purged_new_candidates_18901.xlsx`).

---

### 2. Typo Normalization & Morphological Variance Mapping (`canonical_lemma`)

To prevent spelling typos and inflected morphological variants from fragmenting term frequencies, we instituted a **Canonical Lemma Normalization Protocol** (`canonical_lemma` column):

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

### 3. Human-in-the-Loop Screening Criteria & Adjudication Rules

Every candidate term was evaluated **strictly within its exact sentence context (`example_context`)**:

#### ✅ RETAINED (Gold Emotion Lexicon Codebook: 608 Words)
1. **Experiencer Affective States ($E_1$)**: Direct internal emotional/psychological states felt by the tourist (*nervous*, *awe*, *secure*, *uncomfortable*, *grateful*, *happy*, *afraid*, *thrilled*, *calming*, *annoying*, *stressful*, *tranquil*, *claustrophobia*, *jitters*, *overjoyed*, *ecstasy*).
2. **Stimulus / Service Appraisals ($E_2$)**: Subjective evaluations of air tour attributes (*scary*, *spectacular*, *smooth*, *professional*, *flawless*, *hostile*, *nerve-wracking*, *great*, *amazing*, *good*, *awesome*, *excellent*, *captivating*, *daunting*, *harrowing*).
3. **Aesthetic Emotions & High-Arousal Awe**: *breathtakingly* (expressing intense awe/amazement in air tour context), *sublime* (aesthetic awe over glacier landscapes).

#### ❌ PURGED (Master Removed Non-Emotion Log: 8,118 Words)
1. **Interjections & Emotive Exclamations**: `yay` (purged as an informal interjection rather than a formal emotion noun/adjective).
2. **Temporal & Procedural Performance**: `timely` (purged as objective time/punctuality control).
3. **Physical Vibration & Ride Sensation**: `choppy` (purged as physical flight sensation rather than internal emotion).
4. **Price & Monetary Attributes**: `overpriced`, `inexpensive` (purged as economic cost evaluation).
5. **Operational Smoothness & Degree Modifiers**: `seamlessly` (procedural flow), `invaluable` (cognitive value rating), `beyond` (degree modifier).
6. **Social Formality & Courtesy Greetings**: *thanks*, *thank*, *thanked*, *thankyou*.
7. **Neutral Nature, Objects & Mechanics**: *helicopter*, *plane*, *pilot*, *glacier*, *canyon*, *water*, *blue*, *gold*.

---

### 4. Mathematical Partition Completeness
$$\\text{Total Screened Vocabulary Universe (8,726)} = \\text{Master Gold Lexicon (608)} + \\text{Master Removed Log (8,118)}$$
$$\\text{Master Gold Lexicon (608)} \\cap \\text{Master Removed Log (8,118)} = 0 \\quad (\\text{100% Zero-Overlap Guaranteed Partition})$$

---

### 📂 5. Derived Artifacts & File Directory Guide

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

### 💻 6. Reproduction & Pipeline Execution Commands

To re-run the emotion lexicon induction pipeline or reproduce the Stage Final candidate extraction:

```bash
# 1. Run Stage Final Candidate Extraction & Induction Script
python3 research_modules/emotion_lexicon_induction/scripts/build_stage_final_codebook.py

# 2. Run Data Processing & Feature Engineering Pipeline
python3 run_data_pipeline.py

# 3. Run Level 3 Econometric Regressions & Mitigation Models
python3 run_incongruence_econometrics.py
```"""

lines = readme_path.read_text(encoding="utf-8").splitlines()
start_idx = None
end_idx = None

for idx, l in enumerate(lines):
    if "## 🔬 Corpus-Derived Emotion Lexicon Codebook" in l or "## 🔬 Master Gold Emotion Lexicon Codebook" in l:
        start_idx = idx
    elif start_idx is not None and end_idx is None and l.startswith("## 📈 Summary Data"):
        end_idx = idx

if start_idx is not None and end_idx is not None:
    updated_content = "\n".join(lines[:start_idx]) + "\n" + new_section + "\n\n" + "\n".join(lines[end_idx:])
    readme_path.write_text(updated_content, encoding="utf-8")
    print("Successfully updated README.md!")
else:
    print(f"Warning: start_idx={start_idx}, end_idx={end_idx}")
