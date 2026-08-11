# Module 1: Fine-Grained Emotion Discovery

This module searches for recurring emotion-bearing patterns in the TripAdvisor low-altitude tourism corpus without defining the final “+3” emotions in advance. NRC8 is preserved as the baseline. CATE-107 and GoEmotions are used only after the initial corpus-driven clustering, as reference and review aids.

No original CSV/XLSX is modified. All generated artifacts stay under this module's `outputs/` directory.

## Authoritative corpus

The only review dataset consumed by Stage 1 is:

`research_modules/canonical_pipeline_v2/outputs/canonical/canonical_reviews_v2.csv`

Stage 1 validates unique `review_id`, ISO language state, the English flag, and complete NRC8 availability before segmentation. The current corpus contains 21,215 English reviews, 126,773 sentences, and 138,314 sentence/clause analysis spans. Non-English and uncertain reviews remain in audit files.

Ratings, rating prediction, causal inference, SHAP, econometrics, and final AEM/Emotion Transition modeling are outside this module.

## Stages

1. `prepare`: validate canonical v2, retain its English reviews, and segment reviews with exact source offsets.
2. `embed`: create normalized embeddings with pinned `BAAI/bge-small-en-v1.5` revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` using ONNX CPU inference.
3. `handoff`: prove canonical-English IDs, NRC8 values, spans, embedding index, and embedding matrix align.
4. `cluster`: run seeded PCA/UMAP/HDBSCAN experiments on the full corpus. PCA, each UMAP result, and each HDBSCAN run have interruption-safe caches.
5. `report`: create corpus phrase summaries, stability measures, diverse nearest examples, NRC/VADER post-cluster references, plots, and a review queue.
6. `focused`: repeat discovery on spans selected by exact words from the sole approved CATE-107 workbook. CATE terms select a broad appraisal pool; they are not emotion labels.
7. `reference`: profile the already-obtained cluster examples with pinned `SamLowe/roberta-base-go_emotions-onnx` revision `90ee0c1c4796d370e68968687b8ba51fc11224f4`. All 28 continuous probabilities are stored; none is treated as gold or an automatic “+3” decision.
8. `review`: create a double-coding XLSX/CSV packet. Human fields are deliberately blank until independent review and adjudication.

## Setup and execution

Use the repository-level environment described in `RESEARCH_PIPELINE_V2.md`, then run from this directory:

```bash
python scripts/run_all.py
```

Or run individual stages:

```bash
python scripts/01_prepare_corpus.py
python scripts/02_embed_spans.py
python scripts/03_cluster_from_canonical_v2.py
python scripts/04_report_clusters.py
python scripts/05_focused_discovery.py
python scripts/06_goemotions_reference.py
python scripts/07_build_review_packet.py
```

A current stage is skipped. A stale stage refuses to mix incompatible artifacts. `--force` replaces only this module's generated stage outputs. Do not use `run_all.py --force` unless intentionally recomputing embeddings and all clustering experiments.

## Current outputs and interpretation

The full experiment selected 92 clusters with 91,428 clustered spans and 46,886 retained HDBSCAN noise spans. The CATE-focused view selected 27 clusters from 14,478 candidate spans, with 11,229 clustered and 3,249 retained as noise.

The two experiments show that generic semantic embeddings strongly organize aspects, people, products, recommendation templates, price/worth appraisals, scenery appraisals, and small-aircraft anxiety. Therefore, a cluster is not automatically an emotion. The reporting field `automated_screening_score` only ranks review priority.

The post-cluster GoEmotions stage analyzes 1,190 cluster-example links representing 1,173 unique spans, produces 119 continuous cluster profiles, and records zero truncations. The model is a Reddit-trained reference taxonomy; its values are not corpus-discovered categories.

The principal human-review file is:

`outputs/human_review/module1_cluster_review_packet.xlsx`

It contains instructions, a cluster-type codebook, all 119 cluster rows, 1,190 diverse representative examples, stability evidence, NRC references where available, and GoEmotions reference profiles. Final “+3” selection occurs only after independent coding, adjudication, and consolidation of semantically equivalent clusters.

## Output map

```text
outputs/
├── audit/                 # excluded, uncertain, noise, join, and truncation records
├── clusters/              # full-corpus assignments, stability, grid metrics, caches
├── embeddings/            # ordered span index and cached BGE embeddings
├── focused/               # CATE-107 appraisal-subset experiment
├── human_review/          # independent coding template and XLSX packet
├── intermediate/          # canonical English corpus, sentences, clauses
├── manifests/             # input/config/environment fingerprints for every stage
├── plots/                 # UMAP, stability, and NRC reference figures
├── reference/goemotions/  # span probabilities and 119 cluster profiles
└── reports/               # cluster inventory, diverse examples, and review queue
```

## Verification

Run from the repository root:

```bash
pytest -q
```

Tests cover stable IDs, order-independent joins, language uncertainty, exact offsets, adversative clause splitting, CATE source validation, representative-example diversity, cluster alignment, continuous GoEmotions aggregation, review-packet joins, master overwrite prevention, and canonical handoff invariants.

References: [GoEmotions paper](https://aclanthology.org/2020.acl-main.372/), [GoEmotions model card](https://huggingface.co/SamLowe/roberta-base-go_emotions), [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5), [scikit-learn HDBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html).
