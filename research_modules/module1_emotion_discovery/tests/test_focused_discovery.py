from emotion_discovery.focused_discovery import build_cate_pattern, match_cate_terms


def test_cate_selector_uses_exact_words_not_substrings():
    pattern = build_cate_pattern(["calm", "ease", "worth"])
    assert match_cate_terms("The calm flight put us at ease and was worth it.", pattern) == [
        "calm",
        "ease",
        "worth",
    ]
    assert match_cate_terms("The staircase was worthwhile.", pattern) == []


def test_cate_selector_is_case_insensitive_and_deduplicated():
    pattern = build_cate_pattern(["EPIC", "epic"])
    assert match_cate_terms("Epic, truly EPIC.", pattern) == ["epic"]
