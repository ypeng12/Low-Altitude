# Repository audit before Module 1 implementation

Audit date: 2026-08-10. The audit was read-only. Existing modified and deleted working-tree files were not restored, overwritten, or reformatted.

## Existing pipeline

1. Forty-six raw TripAdvisor CSV files share a 13-column review schema and contain 28,918 rows.
2. `merge_data.py` merges raw files. `clean_level1.py` normalizes text, drops administrative columns, and removes duplicate review identities based on user and normalized review text, leaving 22,235 rows.
3. Several scripts implement different generations of language detection. They do not agree.
4. `clean_level2.py` and the integrated `run_data_pipeline.py` add VADER, text-shape, location, tourism-domain, role/coreference, discourse, and legacy rule-based fields.
5. `run_level3_econometrics.py` separately computes NRC density features. The stored Level 3 file has the eight NRC emotions plus NRC positive/negative.
6. Word-level NRC/CATE scripts, figures, and later regression/audit scripts consume these derivatives.

All principal 22,235-row cleaned datasets contain the same 22,235 unique normalized review identities, although row order and feature generations differ. This permits a safe identity join.

## Data source decision

Use the current `tripadvisor_processed_master.csv` only for text and identity, and attach the existing eight NRC columns from `tripadvisor_level3_econometrics.csv` by stable review ID. Do not run legacy scripts that rewrite either file. Re-audit language with the repository's existing FastText model and preserve every exclusion decision.

## Observed data-quality and engineering risks

- Language lineage drift: the current master marks 21,269 reviews English; Level 3 marks 21,581; a prior FastText generation marked about 21,237. Current labels use full names while other code expects ISO codes.
- One later extraction script checks `language != "en"` against a master using `"English"`, which incorrectly routes thousands of English reviews to an error/other category. That script is outside Module 1 and is not changed here.
- NRC is not stored in the current master. The NRC source is a separate, older feature generation and must be joined by identity rather than order.
- 718 reviews have zero density for all eight NRC emotions. They remain in the corpus because a fixed lexicon miss is relevant evidence for fine-grained discovery.
- Existing word-level reporting forces multi-label NRC words into a single priority category, and some plots assign unclassified words to `trust`. Module 1 retains the eight continuous NRC dimensions instead.
- Cross-file deduplication is order-sensitive. Of 6,682 duplicate-comparison rows in the deletion audit, 6,649 are cross-tour; unsorted glob order can therefore change the retained `tour_name`. Tour identity is not used to discover Module 1 clusters.
- Tour-name parsing retains inconsistent numbering/date suffixes: 46 files become 45 raw tour names and 36 current-master tour names.
- Review text is complete after cleaning: 22,235 unique texts, no empty reviews, and no normalized-text duplicates. Sixteen reviews contain fewer than ten words; they are retained.
- Review length is strongly skewed (median 59 words, 99th percentile about 376, maximum 1,822). Sentence/run-on splitting plus embedding truncation audit is therefore required.
- Ratings are extremely imbalanced (about 93.9% five-star). Module 1 does not use ratings.
- Several README/report counts are stale. For example, documented language and price-mention totals disagree with current stored data.
- `merge_and_clean.py` is empty; multiple scripts execute work at import time; several paths are hard-coded; some scripts download NLTK resources dynamically; there is no repository dependency lock.
- The global environment has NumPy 2.0.2 but matplotlib extensions built against NumPy 1.x. Transformer, UMAP, and pytest packages were absent at audit time. Module 1 therefore uses a documented isolated environment with `numpy<2`.
- Existing tests are demonstrations rather than isolated unit tests and may print or download data at import time.

## Scope boundary

Module 1 does not repair legacy language columns, tour names, ABSA fields, rating models, econometric scripts, or later taxonomies. Those observations are recorded to prevent accidental reuse. Module 2 is planned but is not implemented in this stage.
