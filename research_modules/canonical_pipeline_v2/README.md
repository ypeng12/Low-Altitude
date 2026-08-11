# Canonical research data pipeline v2

This package creates the immutable analysis layer used by the new emotion research modules. It never writes to an original dataset. Generated files are confined to `research_modules/canonical_pipeline_v2/outputs/`.

## What it fixes

- Creates deterministic `review_id` values from normalized reviewer and review text.
- Runs one FastText language audit using ISO codes, probabilities, top-three predictions, and an explicit `uncertain` state.
- Joins NRC8 by `review_id`, never row position, and distinguishes a valid all-zero NRC row from a missing join.
- Reads raw tour files in fixed filename order and represents review–tour attribution as a many-to-many link table.
- Rebuilds the legacy mechanism taxonomy without sending English reviews to multilingual Type 9 merely because `language == "en"`.
- Audits membership and field drift across Level 1, Level 2, Level 3, and master.
- Validates only `data/derived_outputs/cate_words_curated_107_translated.xlsx` as the approved 107-term CATE source.

## Authoritative inputs

- `data/cleaned_datasets/tripadvisor_processed_master.csv`: review text and existing master features.
- `data/cleaned_datasets/tripadvisor_level1_cleaned.csv`, `tripadvisor_level2_features.csv`, and `tripadvisor_level3_econometrics.csv`: drift audits; Level 3 also supplies the existing NRC8 baseline.
- `02-07-2025-TripAdvisor/*.csv`: tour provenance, read in sorted order.
- `lid.176.bin`: FastText language identification.
- `data/derived_outputs/cate_words_curated_107_translated.xlsx`: the sole approved CATE workbook.

## Run

From the repository root, after installing `requirements-research.txt`:

```bash
python research_modules/canonical_pipeline_v2/scripts/build_canonical_v2.py \
  --config research_modules/canonical_pipeline_v2/config/default.json
```

The command skips only when all input fingerprints match and all required outputs exist. `--force` replaces generated v2 outputs only; it does not modify original data.

## Main outputs

- `outputs/canonical/canonical_reviews_v2.csv`: one row per stable review.
- `outputs/provenance/review_tour_links_v2.csv`: many-to-many review–tour links.
- `outputs/provenance/raw_review_occurrences_v2.csv`: every raw occurrence and source file.
- `outputs/audit/language_audit_v2.csv`: ISO language, confidence, uncertainty, and old/new disagreement.
- `outputs/audit/nrc_join_issues_v2.csv`: missing/extra NRC joins.
- `outputs/audit/taxonomy_corrections_v2.csv`: every changed mechanism classification.
- `outputs/audit/dataset_field_drift_{summary,details}_v2.csv`: cross-generation drift.
- `outputs/legacy_rebuild/*.csv`: repaired outputs with `_v2`; no legacy master overwrite.
- `outputs/manifests/canonical_v2.json`: input hashes, versions, and run summary.

The verified current build contains 22,235 canonical reviews: 21,215 English, 995 non-English, and 25 uncertain. It has zero NRC join issues, 28,751 review–tour links, and 6,435 reviews linked to multiple tours. Of 6,607 legacy Type 9 reviews, 5,834 are reclassified; 995 remain Type 9 under the repaired rule.
