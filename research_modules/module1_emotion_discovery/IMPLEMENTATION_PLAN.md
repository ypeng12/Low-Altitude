# Research module execution plan

## Implemented now: Module 1

```text
research_modules/module1_emotion_discovery/
├── config/default.json
├── src/emotion_discovery/
│   ├── config.py
│   ├── ids.py
│   ├── storage.py
│   ├── language.py
│   ├── segmentation.py
│   ├── prepare.py
│   ├── embeddings.py
│   ├── clustering.py
│   ├── reporting.py
│   └── cli.py
├── scripts/{01_prepare_corpus,02_embed_spans,03_cluster_embeddings,04_report_clusters,run_all}.py
├── tests/
├── requirements.txt
├── pyproject.toml
└── outputs/
```

Execution order is preparation/audit, transformer embedding cache, UMAP/HDBSCAN grid and stability analysis, then corpus-derived cluster interpretation and plots. Each stage fingerprints its direct dependencies and refuses stale mixtures.

## Planned later: Module 2

No Module 2 files are created in the current implementation. The proposed structure is:

```text
research_modules/module2_emotion_transformation/
├── config/default.json
├── src/emotion_transformation/
│   ├── candidate_extraction.py
│   ├── discourse.py
│   ├── paired_embeddings.py
│   ├── transformation_induction.py
│   ├── posthoc_typing.py
│   ├── matrix.py
│   ├── reporting.py
│   └── cli.py
├── scripts/
│   ├── 01_extract_candidates.py
│   ├── 02_embed_span_pairs.py
│   ├── 03_induce_transformations.py
│   └── 04_report_matrix.py
├── tests/
└── outputs/
```

The later execution plan is to extract explicit and implicit transition candidates, preserve before/after offsets, embed source and target spans, cluster transformation vectors and automatically recurring span-pair patterns, then use lexical polarity shift, contextual reinterpretation, negation/intensification, contrastive discourse, mixed emotion, and reappraisal only as post-induction analytical types. It will produce one row per candidate with uncertainty retained, a source-to-target matrix, and representative examples per frequent transformation. Module 1 cluster centroids and provisional labels can be reference features, not hard constraints.
