# Module 1: Fine-Grained Emotion Discovery

This module discovers recurring emotion-bearing semantic patterns from the TripAdvisor corpus without defining a new emotion inventory in advance. It treats the existing NRC eight-emotion scores and VADER scores only as post-clustering reference signals.

It is isolated from the repository's legacy pipeline: no original CSV or script is modified, and all generated artifacts stay under `outputs/`.

## Inputs and lineage

- `data/cleaned_datasets/tripadvisor_processed_master.csv` is the immutable source for review text and stable review identity.
- `data/cleaned_datasets/tripadvisor_level3_econometrics.csv` supplies the existing NRC `joy`, `trust`, `anticipation`, `surprise`, `fear`, `sadness`, `disgust`, and `anger` density columns.
- `lid.176.bin` supplies a fresh, non-destructive FastText language audit because existing cleaned files contain incompatible generations of language labels.
- NRC data are joined by a SHA-256-based `review_id` derived from normalized `user_name + review_text`, never by row position.

Ratings, rating prediction, ABSA, SHAP, causal inference, and econometric variables are not used by this module.

## Method

1. Audit language and join the existing NRC baseline by stable identity.
2. Preserve every source sentence with source character offsets. Use discourse-aware clauses as analysis units only when both sides are substantive; otherwise retain the sentence. Split pathological run-on sentences and audit model-token truncation.
3. Encode spans with the pinned revision of `BAAI/bge-small-en-v1.5` through the Sentence Transformers ONNX CPU backend. Embeddings are normalized and cached with an ordered span index and input fingerprints.
4. Reduce embeddings with seeded PCA and UMAP, then evaluate an HDBSCAN parameter grid over multiple UMAP seeds.
5. Select a configuration from seed agreement, coverage, membership confidence, and silhouette quality. Report per-cluster best-match Jaccard stability across seeds and across the full grid.
6. Induce provisional labels from cluster-distinctive one-to-three-word c-TF-IDF phrases. Only after clusters exist, attach the most enriched NRC parent emotion when applicable.
7. Retain HDBSCAN noise, low-confidence clusters, non-English reviews, uncertain language reviews, unmatched joins, excluded spans, unsampled spans, and model-truncated spans in audit files.

The provisional label is evidence for human interpretation, not a validated emotion category. Clusters may encode topics or experience contexts as well as emotion; `requires_human_label_review` makes that uncertainty explicit.

## Reproducible setup

Use Python 3.10 or 3.11 in an isolated environment. Do not install into the repository's current global Python environment: it contains a NumPy/matplotlib binary incompatibility.

```bash
cd research_modules/module1_emotion_discovery
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
pytest
```

The configured embedding revision is fixed to `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`. Every stage manifest records Python, package, model, input-file, configuration, Git commit, and dirty-worktree information.

## Run each restartable stage

From this module directory:

```bash
python scripts/01_prepare_corpus.py
python scripts/02_embed_spans.py
python scripts/03_cluster_embeddings.py
python scripts/04_report_clusters.py
```

Or run all stages in order:

```bash
python scripts/run_all.py
```

A stage skips work only when its manifest fingerprints match and all required outputs exist. If inputs or configuration changed, it refuses to mix old and new artifacts. Explicitly rebuild only this module's generated outputs with:

```bash
python scripts/run_all.py --force
```

To experiment without changing the recorded default, copy `config/default.json` and pass the copy to any command:

```bash
python scripts/03_cluster_embeddings.py --config config/experiment.json --force
```

The default configuration does not sample the analysis corpus. If `max_analysis_spans` is set for a pilot run, excluded span IDs are saved to `outputs/audit/clustering_not_sampled.csv`.

## Output map

```text
outputs/
├── audit/
│   ├── clustering_not_sampled.csv
│   ├── embedding_truncation_audit.csv
│   ├── excluded_reviews.csv
│   ├── excluded_spans.csv
│   ├── language_audit.csv
│   ├── noise_spans.csv
│   └── nrc_join_audit.csv
├── clusters/
│   ├── cluster_assignments.csv
│   ├── cluster_stability.csv
│   ├── configuration_summary.csv
│   ├── experiment_arrays.npz
│   └── experiment_metrics.csv
├── embeddings/
│   ├── embedding_index.csv
│   └── span_embeddings.npy
├── intermediate/
│   ├── analysis_spans.csv
│   ├── corpus_reviews.csv
│   └── sentences.csv
├── manifests/
│   ├── stage01_prepare.json
│   ├── stage02_embeddings.json
│   ├── stage03_clustering.json
│   └── stage04_reporting.json
├── plots/
│   ├── cluster_stability.png
│   ├── nrc_parent_enrichment.png
│   └── umap_clusters.png
└── reports/
    ├── cluster_inventory.csv
    ├── cluster_nrc_profile.csv
    ├── cluster_representative_examples.csv
    ├── module1_summary.json
    └── uncertain_clusters.csv
```

`cluster_inventory.csv` is the main research table. For each discovered cluster it contains cluster size, unique-review count, corpus-derived provisional label, representative phrases and scores, NRC parent and enrichment when applicable, VADER/NRC reference evidence, membership confidence, embedding coherence, seed and grid stability, combined confidence, and a human-review flag. Exact nearest examples and their parent sentences are stored separately in `cluster_representative_examples.csv`.

## Sanity checks

The tests cover stable identity, order-independent NRC joins, exact sentence/clause offsets, adversative clause splitting, language uncertainty thresholds, cluster-label alignment, and corpus-derived phrase induction. Runtime assertions additionally reject duplicate IDs, failed one-to-one joins, embedding/index misalignment, non-finite embeddings, empty cluster solutions, stale cache mixtures, and missing output files.

## Model and algorithm references

- [BGE small English v1.5 model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- [Sentence Transformers clustering examples](https://sbert.net/examples/sentence_transformer/applications/clustering/README.html)
- [scikit-learn HDBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html)
- [UMAP reproducibility](https://umap-learn.readthedocs.io/en/latest/reproducibility.html)
