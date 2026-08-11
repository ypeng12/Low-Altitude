from canonical_pipeline.tour_links import clean_raw_text, parse_tour_name


def test_tour_name_parser_is_nonempty_for_missing_name():
    value = parse_tour_name("13-98_attraction_product_review_2025-02-27.csv")
    assert value.startswith("Unresolved tour")


def test_tour_name_parser_extracts_human_label():
    value = parse_tour_name("1-Kauai Deluxe Sightseeing Flight_1623_attraction_product_review_2025-02-27.csv")
    assert value == "Kauai Deluxe Sightseeing Flight 1623"


def test_raw_html_cleanup_matches_master_identity_normalization():
    assert clean_raw_text("First<br /><br />Second &amp; third") == "First\n\nSecond & third"
