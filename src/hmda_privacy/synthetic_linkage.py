from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .config import QIConfig
from .risk import equivalence_classes, validate_analysis_frame


@dataclass(frozen=True)
class SyntheticLinkageSummary:
    method: str
    synthetic_records: int
    exact_match_records: int
    exact_match_rate: float
    unique_match_records: int
    unique_match_rate: float
    expected_correct_matches: float
    expected_correct_match_rate: float
    random_seed: int

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def generate_synthetic_auxiliary(
    frame: pd.DataFrame,
    config: QIConfig,
    *,
    records: int,
    random_seed: int = 20260822,
) -> pd.DataFrame:
    """Generate identity-free auxiliary QIs from empirical one-way marginals.

    Columns are sampled independently. This intentionally preserves only one-way
    marginals and therefore does not claim to reproduce joint population structure.
    """
    validate_analysis_frame(frame, config)
    if records < 1:
        raise ValueError("records must be positive")
    rng = np.random.default_rng(random_seed)
    synthetic: dict[str, np.ndarray] = {}
    for field in config.fields:
        values = frame[field].to_numpy()
        synthetic[field] = rng.choice(values, size=records, replace=True)
    return pd.DataFrame(synthetic)


def simulate_synthetic_linkage(
    released: pd.DataFrame,
    config: QIConfig,
    *,
    synthetic_records: int,
    random_seed: int = 20260822,
) -> SyntheticLinkageSummary:
    """Simulate exact linkage and return aggregate metrics only."""
    synthetic = generate_synthetic_auxiliary(
        released, config, records=synthetic_records, random_seed=random_seed
    )
    classes = equivalence_classes(released, config)
    matched = synthetic.merge(classes, on=list(config.fields), how="left", validate="many_to_one")
    exact = matched["k"].notna()
    unique = matched["k"].eq(1)
    expected = (1 / matched.loc[exact, "k"]).sum() if exact.any() else 0.0
    return SyntheticLinkageSummary(
        method="independent_empirical_marginals_exact_match",
        synthetic_records=synthetic_records,
        exact_match_records=int(exact.sum()),
        exact_match_rate=float(exact.mean()),
        unique_match_records=int(unique.sum()),
        unique_match_rate=float(unique.mean()),
        expected_correct_matches=float(expected),
        expected_correct_match_rate=float(expected / synthetic_records),
        random_seed=random_seed,
    )

