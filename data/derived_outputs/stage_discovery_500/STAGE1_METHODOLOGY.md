# Stage 1: 500-Review Discovery Codebook Methodology & Screening Logic

> 📄 **Module Path**: `research_modules/emotion_lexicon_induction/`  
> 🐍 **Primary Execution Scripts**:  
> - Pipeline Runner: `research_modules/emotion_lexicon_induction/scripts/build_emotion_lexicon_stage.py`  
> - Ingestion & Sync: `research_modules/emotion_lexicon_induction/scripts/ingest_ai_responses.py`

---

## 🛠️ 1. Sampling & Candidate Extraction (分层抽样与候选词抽取)

- **Source Corpus**: `data/cleaned_datasets/tripadvisor_level3_english_v2.csv` (21,215 clean English reviews).
- **Sampling Method**: Stratified random sampling ($N=500$, Seed 42), weighted by star ratings, air tour products, aircraft types, and review text lengths (`manifest_500_reviews.csv`).
- **Initial Candidate Pool**: Extracted **3,605 unique candidate lemmas** from tokenization, POS tagging, and lemmatization.

---

## 🔍 2. Sentence-Contextual Screening Logic (结合真实例句的审视逻辑)

### Core Rule: Context-First Adjudication (语境优先原则)
Words are never judged in isolation. Every candidate term was evaluated strictly within its exact review sentence (`example_context`).

### Classification Boundaries & Decisions

#### ✅ RETAINED (Saved in `clean_emotion_words_500_reviews.xlsx` / `.csv` - 347 Words)
1. **Experiencer Affective States ($E_1$)**: Direct internal emotional/psychological states felt by the tourist (*nervous*, *awe*, *secure*, *uncomfortable*, *grateful*, *happy*, *afraid*, *thrilled*, *sick*).
2. **Stimulus / Service Appraisals ($E_2$)**: Subjective evaluations of air tour attributes (*scary*, *breathtaking*, *spectacular*, *smooth*, *professional*, *flawless*, *hostile*, *nerve-wracking*).
3. **Polysemous Affect Terms ($E_1\_E_2$)**: Terms carrying both state and appraisal values depending on sentence context (e.g., *comfortable* - *"made us feel comfortable"* [$E_1$] vs *"comfortable air tour"* [$E_2$]).

#### ❌ PURGED (Moved to `removed_non_emotion_words_from_500_reviews.csv` - 3,258 Words)
1. **Neutral Physical Objects, Colors & Nature**: *blue*, *silver*, *gold*, *tall*, *pine*, *gravel*, *water*, *canyon*, *helicopter*, *plane*.
2. **Physical Verbs & Action Expressions**: *whooping*, *yelled*, *crying*, *screaming*, *smiling*, *wiping*, *writing*, *taxied*, *switched*, *flying*, *landing*.
3. **Cognitive / Speculative Stance Words**: *wondered*, *wonder*, *wonders*, *think*, *thought*, *suspect*, *doubt*, *hesitate*, *assume*, *believe*, *guess*.
4. **Neutral Structural Modifiers, Quantifiers & Adverbs**: *together* (physical seating), *choice* (option), *absolute* (degree), *quickly*, *world*, *custom*, *daily*, *whole*, *different*, *entire*, *due*, *however*, *old*, *later*, *possible*.
5. **Contextually Non-Emotion Polysemes**: *interest* (*"points of interest"*), *shy* (*"one level shy of Heaven"*), *respect* (*"in every respect"*).

---

## 📊 3. Codebook Annotations & Partition Integrity

- **`chinese_translation`**: 100% of retained 347 emotion terms feature precise contextual Chinese translations.
- **`affect_type`**: Explicitly annotated into $E_1$ State, $E_2$ Appraisal, or $E_1\_E_2$ Polysemous.
- **Partition Integrity**:
  $$\text{Total 500 Candidates (3,605)} = \text{Clean Emotion Words (347)} + \text{Removed Non-Emotion Words (3,258)}$$
  Zero overlap ($\text{Clean} \cap \text{Removed} = 0$), 100% mathematical completeness.
