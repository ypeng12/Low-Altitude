# Module 2: Emotion / Semantic Transformation Detection

This module detects narrated source→target changes in the canonical English TripAdvisor corpus. It is separate from Module 1 emotion discovery and from final Gold Standard creation.

The module never edits original data. It reuses Module 1 sentence/clause offsets and pinned BGE embeddings, and writes only under `outputs/`.

## Research boundary

The output represents transformations narrated in review text. A pattern such as `flight apprehension → pilot reassurance → relief` is a textual mechanism attribution, not an econometric or causal effect. Ratings, rating prediction, SHAP, causal inference, and econometrics are not used.

## Pipeline

1. Extract adjacent source/target spans around `but`, `however`, `although`, `though`, `despite`, `yet`, `then`, `still`, `while`, semicolons, and related markers. Exact source offsets are validated against canonical review text.
2. Map both spans to Module 1 embeddings and create an L2-normalized directional vector: `target_embedding - source_embedding`.
3. Run seeded PCA/UMAP/HDBSCAN over pair directions. Every PCA, UMAP, and HDBSCAN result is restart-cached.
4. Induce source and target phrases separately, then report `source phrases → target phrases`, stability, relation purity, diverse examples, and noise.
5. Apply an auditable LLM-assisted post-cluster seed code to strong recurring patterns. This creates a provisional matrix only; unmapped clusters and noise remain uncertain.
6. Build a 300-item blinded double-coding workbook with separate AEM and Emotion Transition sheets. Instance-level LLM predictions and cluster IDs are hidden from annotators.

## Run

From the repository root in the unified environment:

```bash
python research_modules/module2_emotion_transition/scripts/01_extract_candidates.py
python research_modules/module2_emotion_transition/scripts/02_build_pair_vectors.py
python research_modules/module2_emotion_transition/scripts/03_cluster_transformations.py
python research_modules/module2_emotion_transition/scripts/04_report_clusters.py
python research_modules/module2_emotion_transition/scripts/05_provisional_cluster_coding.py
python research_modules/module2_emotion_transition/scripts/06_build_annotation_packet.py
```

Or use `python scripts/run_research_pipeline_v2.py`. Current stages skip; stale stages refuse incompatible output unless that stage is explicitly run with `--force`.

## Current verified result

- 12,285 marker-bearing spans are fully dispositioned: 11,764 candidates and 521 audited leading-marker metadata cases.
- All 11,764 source/target spans map to BGE embeddings; missing rows and zero direction vectors are both 0.
- Twelve clustering experiments select 35 directional clusters containing 4,307 pairs; 7,457 pairs remain HDBSCAN noise.
- Strong recurring patterns include expensive→worth-it, motion-sickness concern→no symptoms, small-plane apprehension→safe/enjoyable, adverse flight sensation→scenic awe, weather loss→disappointment, nervousness→pilot reassurance→relief, and missed landing→continued enjoyment.
- Fourteen clusters / 1,917 pairs have LLM-assisted provisional codes; 21 clusters plus all noise, totaling 9,847 pairs, remain uncertain/unmapped.
- The provisional matrix has eight cells. One mapped cluster is explicitly warned for seed stability below 0.50.
- The annotation packet contains 140 mapped-cluster representatives, 105 unmapped-cluster representatives, and 55 relation-stratified noise pairs. No human field is prefilled and no Gold record exists.

## Key outputs

```text
outputs/
├── candidates/explicit_transition_candidates.csv
├── pair_vectors/{pair_embedding_index.csv,transformation_vectors.npy}
├── clusters/{cluster_assignments.csv,cluster_stability.csv,experiment_metrics.csv}
├── reports/
│   ├── transformation_cluster_inventory.csv
│   ├── transformation_cluster_examples.csv
│   ├── provisional_cluster_codebook.csv
│   ├── structured_transformation_candidates_provisional.csv
│   ├── initial_transformation_matrix_provisional.csv
│   └── frequent_transformation_examples_provisional.csv
├── human_annotation/
│   ├── annotation_sample_300.csv
│   └── aem_transition_blinded_double_coding.xlsx
└── audit/  # exclusions, noise, uncertain/unmapped, and full sampling disposition
```

The final matrix and Gold Standard may be built only after two independent human coders complete the blinded sheets, disagreements are adjudicated, agreement is reported, and Module 1's provisional “+3” inventory is accepted or revised.
