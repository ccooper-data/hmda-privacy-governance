import pandas as pd
import pytest

from hmda_privacy.differential_privacy import dp_group_counts


def test_dp_counts_are_reproducible_nonnegative_and_hide_true_counts() -> None:
    frame = pd.DataFrame({"group": ["A", "A", "B"]})
    first, metadata = dp_group_counts(frame, group_fields=["group"], epsilon=1, random_seed=9)
    second, _ = dp_group_counts(frame, group_fields=["group"], epsilon=1, random_seed=9)
    pd.testing.assert_frame_equal(first, second)
    assert "true_count" not in first
    assert first["dp_count"].ge(0).all()
    assert metadata.mechanism == "laplace"


def test_dp_rejects_nonpositive_epsilon() -> None:
    with pytest.raises(ValueError, match="epsilon must be positive"):
        dp_group_counts(pd.DataFrame({"group": ["A"]}), group_fields=["group"], epsilon=0)

