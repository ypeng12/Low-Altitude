# Low-Altitude research pipeline v2

This is the reproducible entry point for the repaired pre-model data layer, Module 1 emotion discovery, and provisional AEM/Emotion Transition research stages. It does not run rating prediction, causal inference, SHAP, econometrics, or final human coding.

## One environment

Use Python 3.10 or 3.11. Python 3.11 is the tested version.

```bash
cd /Users/yuliangpeng/Desktop/Low-Altitude
python3.11 -m venv .venv-research
source .venv-research/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-research.txt
python -m pip install -e research_modules/canonical_pipeline_v2
python -m pip install -e research_modules/module1_emotion_discovery
python -m pip install -e research_modules/module2_emotion_transition
pytest -q
```

## Run the current pipeline

```bash
python scripts/run_research_pipeline_v2.py
```

The order is canonical v2 → canonical-only corpus preparation → BGE embeddings → Module 1 discovery/reference/review → directional Emotion Transition candidates/vectors/clustering → provisional AEM/Transition seed coding → blinded annotation packet.

Every stage skips when current and refuses stale mixtures. Run or rebuild one stage with:

```bash
python scripts/run_research_pipeline_v2.py --only review
python scripts/run_research_pipeline_v2.py --only focused --force
```

`--only all --force` intentionally recomputes every expensive embedding and clustering stage; it is normally unnecessary.

## Data authority and non-overwrite rule

- Original cleaned data remain under `data/cleaned_datasets/` and are never pipeline outputs.
- The authoritative new review layer is `research_modules/canonical_pipeline_v2/outputs/canonical/canonical_reviews_v2.csv`.
- The only approved CATE input is `data/derived_outputs/cate_words_curated_107_translated.xlsx`.
- New generated datasets use `_v2` names or stay under module `outputs/` directories.
- Three legacy scripts that formerly targeted `tripadvisor_processed_master.csv` now target explicit `*_legacy_rebuild.csv` files instead.

## Current verified invariants

- 22,235 unique canonical reviews and stable review IDs.
- 21,215 English, 995 non-English, and 25 uncertain language decisions with ISO code and confidence retained.
- NRC8 joins have zero missing/extra IDs; 718 all-zero rows are valid no-hit baselines, not missing data.
- 28,918 raw review occurrences map to canonical reviews.
- 28,751 review–tour links; 6,435 reviews have more than one tour link.
- 6,607 legacy Type 9 rows audited; 5,834 are reclassified and 995 remain Type 9.
- Module 1 has 138,314 analysis spans and a byte-identical 138,314 × 384 BGE embedding cache across the canonical-only refactor.
- All discovered clusters and noise examples remain available for review; no uncertain sample is forced into a final label.
- Emotion Transition currently retains 11,764 explicit discourse candidates: 4,307 in 35 directional clusters and 7,457 as noise/uncertain.
- The provisional transition matrix covers 1,917 pairs; 9,847 remain uncertain/unmapped, and no record is marked Gold.

See the README files under `canonical_pipeline_v2`, `module1_emotion_discovery`, and `module2_emotion_transition` for schemas and output maps.
