# Corpus-derived emotion-word lexicon

This module builds a human-validated, AI-assisted unigram emotion lexicon directly from the canonical English TripAdvisor corpus. It deliberately does **not** use NRC, VADER, CATE, GoEmotions, star ratings, or existing sentiment features to decide which words are emotions. External lexicons are permitted only after the corpus-derived lexicon has been frozen.

## Current scope

- Single words only. Phrases, AEM coding, and emotion transitions are later stages.
- The original `review_text` is the discovery text. Titles are preserved for context but are not tokenized into candidates.
- Candidate extraction is deliberately broad: content-word POS classes are retained for AI/human open coding. POS and stopwords reduce clerical work; they do not label emotions.
- A word occurrence is coded in its original review context. The eventual deliverable is still a word/lemma lexicon.
- CATE and all previous `+3` outputs remain legacy baselines and are not inputs.

## Coding statuses

| Code | Meaning | Main lexicon? |
|---|---|---|
| `E1` | Directly names or expresses an experiencer's internal affective state | Yes, after human approval |
| `E2` | Emotion-eliciting or appraisal word | No; auxiliary table |
| `E3` | Bodily or behavioral indicator | No; auxiliary table |
| `N` | Non-emotion occurrence | No |
| `U` | Uncertain or context-dependent | Retain for adjudication |

AI suggestions are never final human decisions. An AI response must select exact supplied token indices; invented or paraphrased words are invalid. Star ratings are used to diversify discovery sampling but are withheld from the AI task and human coding workbook to reduce annotation bias.

## Sampling design

The module filters the canonical table to `analysis_language_status == "english"` and creates one deterministic ranking from stable `review_id` values and seed 42. Rating, primary tour, aircraft type, and fixed review-length bins receive tempered inverse-frequency weights. Consecutive, non-overlapping slices of that ranking create fixed disjoint samples:

```text
500 discovery reviews ∩ 2,000 gold-candidate reviews = 0
500 + 2,000 = 2,500 manually studied reviews
2,500 + 18,715 remaining reviews = 21,215 canonical English reviews
```

This is a maximum-variation discovery sample, not an estimator of population prevalence. Final prevalence must be calculated on the full English corpus, not directly from the oversampled discovery stages. Every weight, rank, tour link, and inclusion flag is saved in `outputs/sampling/disjoint_sample_manifest.csv`.

## Install and run

From the repository root:

```bash
python -m pip install -r requirements-research.txt
python -m nltk.downloader averaged_perceptron_tagger_eng stopwords

python research_modules/emotion_lexicon_induction/scripts/build_emotion_lexicon_stage.py \
  --config research_modules/emotion_lexicon_induction/config/default.json \
  --stage discovery_500
```

After the 500-review human adjudication and codebook revision, generate the entirely new 2,000-review packet with `--stage gold_candidate_2000`. It has no `review_id` overlap with the discovery set. The name `gold_candidate` is deliberate: it becomes Gold Standard only after independent human coding and adjudication.

## Stage-500 outputs

- `stage_discovery_500/sample_discovery_500_reviews.csv`: exact discovery reviews and sampling metadata.
- `stage_discovery_500/unigram_occurrences_discovery_500.csv`: every token with character offsets, POS, lemma, context, and an explicit eligibility reason.
- `stage_discovery_500/unigram_candidates_discovery_500.csv`: one row per eligible lemma with corpus evidence and blank AI/human decision fields.
- `stage_discovery_500/ai_tasks_discovery_500.jsonl`: strict exact-token AI tasks; no model is called silently.
- `stage_discovery_500/emotion_word_codebook_discovery_500.xlsx`: human review workbook with instructions, status definitions, sampled reviews, and unigram candidates.
- `audit/canonical_rows_outside_english_corpus.csv`: all non-English/uncertain canonical rows excluded from discovery.
- `audit/empty_english_review_text.csv`: explicit audit of empty English review bodies.
- `manifests/stage_discovery_500.json`: input/output hashes, versions, seed, counts, and Git state.

## Human + AI protocol

1. AI reads each JSONL task and proposes only `E1`, `E2`, `E3`, or `U` occurrences. It must copy an exact token index.
2. A human checks every proposed `E1`, every `U`, and a random audit sample of omitted tokens.
3. A second human independently codes an agreed subset. Agreement is reported before adjudication.
4. Approved `E1` occurrences are grouped by lemma; polysemous uses remain occurrence-level evidence.
5. New categories are induced after direct emotion words are confirmed. No target such as `8+3` is imposed.
6. NRC/VADER overlap is calculated only after the corpus-derived list and category definitions are frozen.

The current builder creates the auditable packet; it does not claim blank AI/human columns have been validated.

To import model output after it has been saved as one JSON object per review, run:

```bash
python research_modules/emotion_lexicon_induction/scripts/ingest_ai_responses.py \
  --config research_modules/emotion_lexicon_induction/config/default.json \
  --stage discovery_500 \
  --responses /absolute/path/to/ai_responses.jsonl
```

The importer rejects an AI proposal unless its `review_id`, token index, and surface form exactly match the task packet. It writes valid proposals, response errors, and a human adjudication queue as separate audit files; AI approval can never silently become a human decision.

The stage-500 build uses `lowercase_surface` normalization. Inflected forms are deliberately not merged automatically; the workbook provides human lemma/word-family fields for adjudication. This conservative choice avoids introducing an unlogged lexical resource or an incorrect automatic lemma into the new lexicon.
