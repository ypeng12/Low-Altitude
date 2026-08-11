import pandas as pd

from canonical_pipeline.drift import audit_dataset_drift


def test_drift_audit_aligns_by_id_and_reports_cells():
    master = pd.DataFrame(
        {"review_id": ["r1", "r2"], "user_name": ["a", "b"], "review_text": ["x", "y"], "value": [1, 2]}
    )
    shuffled = pd.DataFrame(
        {"review_id": ["r2", "r1"], "user_name": ["b", "a"], "review_text": ["y", "x"], "value": [3, 1]}
    )
    membership, summary, details = audit_dataset_drift(master, {"other": shuffled})
    assert membership.loc[0, "missing_from_dataset"] == 0
    assert summary.loc[summary["field"].eq("value"), "different_rows"].item() == 1
    assert details.loc[0, "review_id"] == "r2"
