import pandas as pd

from canonical_pipeline.build import NRC_COLUMNS, join_language, join_nrc


def test_nrc_join_uses_review_id_not_row_order():
    master = pd.DataFrame({"review_id": ["r1", "r2"], "review_text": ["one", "two"]})
    rows = []
    for review_id, value in [("r2", 2.0), ("r1", 1.0)]:
        rows.append({"review_id": review_id, **{column: value for column in NRC_COLUMNS}})
    joined, audit = join_nrc(master, pd.DataFrame(rows))
    assert audit.empty
    assert joined.set_index("review_id").loc["r1", "nrc_joy"] == 1.0


def test_language_join_preserves_iso_confidence_and_uncertain():
    master = pd.DataFrame({"review_id": ["r1"]})
    language = pd.DataFrame(
        {
            "review_id": ["r1"],
            "fasttext_label": ["en"],
            "fasttext_probability": [0.55],
            "language_decision": ["uncertain"],
            "top_k_predictions": ["en:0.55;de:0.40"],
        }
    )
    joined = join_language(master, language)
    assert joined.loc[0, "language_iso"] == "en"
    assert joined.loc[0, "language_confidence"] == 0.55
    assert joined.loc[0, "analysis_language_status"] == "uncertain"
    assert not bool(joined.loc[0, "analysis_is_english"])
