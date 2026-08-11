from pathlib import Path

from canonical_pipeline.cate import CATE_COLUMNS, validate_cate_workbook


def test_approved_cate_workbook_is_exactly_107_unique_terms():
    root = Path(__file__).resolve().parents[3]
    path = root / "data/derived_outputs/cate_words_curated_107_translated.xlsx"
    frame, audit = validate_cate_workbook(path)
    assert len(frame) == 107
    assert tuple(frame.columns) == CATE_COLUMNS
    assert audit["unique_english_terms"] == 107
