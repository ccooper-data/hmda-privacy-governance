from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class QIConfig:
    version: int
    name: str
    fields: tuple[str, ...]
    forbidden_direct_identifiers: tuple[str, ...]
    sensitive_attributes: tuple[str, ...]
    minimum_cell_size: int
    k_thresholds: tuple[int, ...]


def load_qi_config(path: str | Path) -> QIConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    fields = tuple(raw["fields"])
    forbidden = tuple(raw["forbidden_direct_identifiers"])
    overlap = sorted(set(fields) & set(forbidden))
    if overlap:
        raise ValueError(f"Direct identifiers cannot be quasi-identifiers: {overlap}")
    reporting = raw["reporting"]
    return QIConfig(
        version=int(raw["version"]),
        name=str(raw["name"]),
        fields=fields,
        forbidden_direct_identifiers=forbidden,
        sensitive_attributes=tuple(raw["sensitive_attributes"]),
        minimum_cell_size=int(reporting["minimum_cell_size"]),
        k_thresholds=tuple(int(value) for value in reporting["k_thresholds"]),
    )

