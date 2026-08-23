from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

COUNT_FIELDS = {
    "record_count",
    "records",
    "reference_n",
    "comparison_n",
    "reference_n_k5",
    "comparison_n_k5",
    "sample_unique_records",
    "observed_equivalence_classes",
}
SAFE_LABEL_FIELDS = {
    "configuration",
    "method",
    "qi_tier",
    "derived_race",
    "derived_ethnicity",
    "residential_density_quintile",
    "release_density_quintile",
    "utility_status",
    "status",
}


def enforce_minimum_cell(value: Any, *, minimum_cell_size: int) -> Any:
    """Redact an aggregate record whenever any declared contributing cell is too small."""
    if minimum_cell_size < 2:
        raise ValueError("minimum_cell_size must be at least two")
    if isinstance(value, Mapping):
        small_fields = [
            key
            for key, item in value.items()
            if key in COUNT_FIELDS
            and isinstance(item, (int, float))
            and not isinstance(item, bool)
            and item < minimum_cell_size
        ]
        if small_fields:
            redacted = {key: value[key] for key in SAFE_LABEL_FIELDS if key in value}
            redacted.update(
                {
                    "suppression_status": "suppressed_minimum_cell",
                    "minimum_cell_size": minimum_cell_size,
                }
            )
            return redacted
        return {
            key: enforce_minimum_cell(item, minimum_cell_size=minimum_cell_size)
            for key, item in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [enforce_minimum_cell(item, minimum_cell_size=minimum_cell_size) for item in value]
    return value
