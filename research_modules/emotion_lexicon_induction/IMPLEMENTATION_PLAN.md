# Implementation plan

1. **Discovery 500 — open coding.** Create the immutable first 500-review slice, extract auditable unigram occurrences, obtain AI proposals, and adjudicate direct emotion words into draft codebook v0.1.
2. **Disjoint 2,000 — Gold Standard candidate.** Code a new 2,000-review slice with zero `review_id` overlap with the first 500. Two human coders independently label the agreed portion, adjudicate disagreements, measure agreement, and then freeze Gold Codebook v1.0. The 2,000 rows are not called Gold before this occurs.
3. **Full English corpus — application.** Apply the frozen word/sense rules to the remaining corpus and all 21,215 reviews, retain unknown and uncertain occurrences, and audit a probability sample of automatic exclusions.
4. **Post-hoc comparison.** Only after the lexicon is frozen, compare its terms, uses, and induced categories with NRC and VADER. Existing CATE and provisional `+3` artifacts remain legacy references.
5. **Later research modules.** Build phrases, Aspect–Emotion–Mechanism coding, and Emotion Transition on top of the validated unigram foundation.

Human annotation is a required stage gate. An AI-only file must never be renamed or reported as the final human-validated lexicon.
