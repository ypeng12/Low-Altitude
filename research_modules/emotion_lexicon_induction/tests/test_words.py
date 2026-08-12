from __future__ import annotations

import nltk

from emotion_lexicon.words import coarse_pos, extract_review_tokens


def test_coarse_pos_mapping() -> None:
    assert coarse_pos("JJ") == "ADJ"
    assert coarse_pos("RB") == "ADV"
    assert coarse_pos("NN") == "NOUN"
    assert coarse_pos("NNP") == "PROPN"
    assert coarse_pos("VBD") == "VERB"


def test_offsets_and_context_are_preserved(monkeypatch) -> None:
    monkeypatch.setattr(nltk, "pos_tag", lambda words, lang="eng": [(word, "JJ") for word in words])

    monkeypatch.setattr("emotion_lexicon.words.stopwords.words", lambda language: ["i", "was"])
    text = "I was nervous. The weather was calm."
    records = extract_review_tokens(
        "review_1",
        text,
        minimum_letters=2,
        eligible_coarse_pos={"ADJ", "ADV", "NOUN", "VERB"},
        maximum_context_characters=200,
    )
    nervous = next(record for record in records if record.normalized_word == "nervous")
    calm = next(record for record in records if record.normalized_word == "calm")
    assert text[nervous.char_start : nervous.char_end] == "nervous"
    assert nervous.context == "I was nervous."
    assert calm.context == "The weather was calm."
    assert nervous.candidate_eligible


def test_proper_nouns_are_audited_but_not_eligible(monkeypatch) -> None:
    monkeypatch.setattr(nltk, "pos_tag", lambda words, lang="eng": [(word, "NNP") for word in words])

    monkeypatch.setattr("emotion_lexicon.words.stopwords.words", lambda language: [])
    records = extract_review_tokens(
        "review_2",
        "Denali",
        minimum_letters=2,
        eligible_coarse_pos={"ADJ", "ADV", "NOUN", "VERB"},
        maximum_context_characters=200,
    )
    assert len(records) == 1
    assert not records[0].candidate_eligible
    assert records[0].eligibility_reason == "ineligible_pos:PROPN"


def test_curly_apostrophe_surface_remains_exact(monkeypatch) -> None:
    monkeypatch.setattr(nltk, "pos_tag", lambda words, lang="eng": [(word, "JJ") for word in words])
    monkeypatch.setattr("emotion_lexicon.words.stopwords.words", lambda language: [])
    text = "I’m thrilled."
    records = extract_review_tokens(
        "review_3",
        text,
        minimum_letters=2,
        eligible_coarse_pos={"ADJ", "ADV", "NOUN", "VERB"},
        maximum_context_characters=200,
    )
    first = records[0]
    assert first.surface == "I’m"
    assert text[first.char_start : first.char_end] == first.surface
    assert first.normalized_word == "i'm"
