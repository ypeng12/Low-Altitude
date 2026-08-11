from emotion_discovery.segmentation import clause_spans, segment_review, sentence_spans


def test_sentence_offsets_preserve_source_text_and_abbreviation():
    text = "Dr. Smith was nervous at first, but the pilot reassured us. Amazing!"
    spans = sentence_spans(text)
    assert [span.text for span in spans] == [
        "Dr. Smith was nervous at first, but the pilot reassured us.",
        "Amazing!",
    ]
    assert all(text[span.start : span.end] == span.text for span in spans)


def test_contrastive_clause_split_is_data_preserving_with_parent_context():
    text = "I was nervous at first, but the pilot quickly reassured us."
    sentence = sentence_spans(text)[0]
    clauses = clause_spans(sentence, text, min_tokens=3)
    assert [clause.text for clause in clauses] == [
        "I was nervous at first,",
        "the pilot quickly reassured us.",
    ]
    assert clauses[1].marker_before == "but"
    assert all(text[clause.start : clause.end] == clause.text for clause in clauses)


def test_leading_subordinator_splits_at_comma():
    text = "Although it looked genuinely scary, the flight felt wonderfully thrilling."
    sentence = sentence_spans(text)[0]
    clauses = clause_spans(sentence, text, min_tokens=3)
    assert [clause.text for clause in clauses] == [
        "it looked genuinely scary",
        "the flight felt wonderfully thrilling.",
    ]
    assert clauses[0].marker_before == "although"


def test_segment_review_uses_clauses_only_where_viable():
    text = "Amazing! I was nervous, but the pilot was calm and reassuring."
    sentences, spans, excluded = segment_review("review_x", text)
    assert len(sentences) == 2
    assert [span["unit_type"] for span in spans] == ["sentence", "clause", "clause"]
    assert not excluded
    assert len({span["span_id"] for span in spans}) == len(spans)
