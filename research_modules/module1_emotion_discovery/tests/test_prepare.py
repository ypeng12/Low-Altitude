import pandas as pd

from emotion_discovery.prepare import NRC_COLUMNS, join_nrc_baseline


def test_nrc_join_uses_review_id_not_row_order():
    master = pd.DataFrame(
        {
            "review_id": ["r1", "r2"],
            "review_title": ["one", "two"],
            "tour_name": ["a", "b"],
        }
    )
    nrc = pd.DataFrame({"review_id": ["r2", "r1"]})
    for index, column in enumerate(NRC_COLUMNS):
        nrc[column] = [index + 2.0, index + 1.0]
    joined, audit = join_nrc_baseline(master, nrc)
    assert audit.empty
    assert joined.loc[joined["review_id"] == "r1", NRC_COLUMNS[0]].item() == 1.0
    assert joined.loc[joined["review_id"] == "r2", NRC_COLUMNS[0]].item() == 2.0
