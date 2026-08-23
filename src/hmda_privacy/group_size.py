from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

BLACK = "Black or African American"
WHITE = "White"
NON_HISPANIC = "Not Hispanic or Latino"
GROUP_SIZE_BINS = [0, 1, 2, 4, 9, 19, 49, 99, np.inf]
GROUP_SIZE_LABELS = ["1", "2", "3-4", "5-9", "10-19", "20-49", "50-99", "100+"]


@dataclass(frozen=True)
class PermutationResult:
    observed_ratio: float
    null_mean: float
    null_std: float
    null_ci_low: float
    null_ci_high: float
    p_value_two_sided: float
    iterations: int
    seed: int


def _normalized(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame[columns].copy()
    for column in columns:
        result[column] = result[column].astype("string").fillna("<MISSING>")
    return result


def score_demographic_uniqueness(frame: pd.DataFrame) -> pd.DataFrame:
    keys = [
        "census_tract",
        "applicant_age",
        "applicant_sex",
        "derived_race",
        "derived_ethnicity",
    ]
    scored = _normalized(frame, keys)
    scored["k"] = scored.groupby(keys, observed=True, sort=False)[keys[0]].transform("size")
    scored["is_unique"] = scored["k"].eq(1)
    scored["n_group"] = scored.groupby(
        ["census_tract", "derived_race", "derived_ethnicity"], observed=True, sort=False
    )["census_tract"].transform("size")
    return scored


def uniqueness_by_group_size(scored: pd.DataFrame, *, minimum_cell_size: int) -> list[dict]:
    focal = scored.loc[
        scored["derived_race"].isin([BLACK, WHITE]) & scored["derived_ethnicity"].eq(NON_HISPANIC)
    ].copy()
    focal["group_size_bin"] = pd.cut(
        focal["n_group"], bins=GROUP_SIZE_BINS, labels=GROUP_SIZE_LABELS, include_lowest=True
    )
    rows = []
    for (size_bin, race), group in focal.groupby(
        ["group_size_bin", "derived_race"], observed=True, sort=False
    ):
        if len(group) < minimum_cell_size:
            continue
        rows.append(
            {
                "group_size_bin": str(size_bin),
                "derived_race": str(race),
                "record_count": len(group),
                "unique_records": int(group["is_unique"].sum()),
                "sample_uniqueness_rate": float(group["is_unique"].mean()),
            }
        )
    return rows


def size_matched_ratio(
    scored: pd.DataFrame,
    *,
    tolerance_ratio: float = 1.20,
    bootstrap_replicates: int = 2_000,
    seed: int = 20_260_823,
) -> dict:
    focal = scored.loc[
        scored["derived_race"].isin([BLACK, WHITE]) & scored["derived_ethnicity"].eq(NON_HISPANIC)
    ]
    counts = focal.groupby(["census_tract", "derived_race"], observed=True).size().unstack()
    counts = counts.dropna(subset=[BLACK, WHITE])
    matched = counts.loc[
        counts[[BLACK, WHITE]].max(axis=1) / counts[[BLACK, WHITE]].min(axis=1) <= tolerance_ratio
    ]
    selected = focal.loc[focal["census_tract"].isin(matched.index)]
    rates = selected.groupby("derived_race", observed=True)["is_unique"].agg(["size", "mean"])
    estimable = (
        BLACK in rates.index and WHITE in rates.index and float(rates.loc[WHITE, "mean"]) > 0
    )
    bootstrap_ci: tuple[float, float] | None = None
    if len(matched) and BLACK in rates.index and WHITE in rates.index:
        tract_stats = (
            selected.groupby(["census_tract", "derived_race"], observed=True)["is_unique"]
            .agg(["size", "sum"])
            .unstack(fill_value=0)
        )
        rng = np.random.Generator(np.random.PCG64(seed))
        boot = []
        for _ in range(bootstrap_replicates):
            draw = rng.integers(0, len(tract_stats), size=len(tract_stats))
            sampled = tract_stats.iloc[draw]
            black_rate = sampled[("sum", BLACK)].sum() / sampled[("size", BLACK)].sum()
            white_rate = sampled[("sum", WHITE)].sum() / sampled[("size", WHITE)].sum()
            if white_rate > 0:
                boot.append(float(black_rate / white_rate))
        if boot:
            bootstrap_ci = (float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975)))
    return {
        "matching_tolerance_ratio": tolerance_ratio,
        "matched_tracts": len(matched),
        "black_records": int(rates.loc[BLACK, "size"]) if BLACK in rates.index else 0,
        "white_records": int(rates.loc[WHITE, "size"]) if WHITE in rates.index else 0,
        "black_uniqueness": float(rates.loc[BLACK, "mean"]) if BLACK in rates.index else None,
        "white_uniqueness": float(rates.loc[WHITE, "mean"]) if WHITE in rates.index else None,
        "uniqueness_ratio": (
            float(rates.loc[BLACK, "mean"] / rates.loc[WHITE, "mean"]) if estimable else None
        ),
        "bootstrap_replicates": bootstrap_replicates,
        "bootstrap_seed": seed,
        "ratio_ci_low": bootstrap_ci[0] if bootstrap_ci else None,
        "ratio_ci_high": bootstrap_ci[1] if bootstrap_ci else None,
        "underpowered": bool(
            len(matched) < 20
            or BLACK not in rates.index
            or WHITE not in rates.index
            or rates.loc[BLACK, "size"] < 100
            or rates.loc[WHITE, "size"] < 100
        ),
    }


def permutation_null(
    scored: pd.DataFrame, *, iterations: int = 1_000, seed: int = 20_260_823
) -> PermutationResult:
    if iterations < 1:
        raise ValueError("iterations must be positive")
    work = scored.reset_index(drop=True)
    focal_code = np.where(
        work["derived_ethnicity"].eq(NON_HISPANIC) & work["derived_race"].eq(BLACK),
        1,
        np.where(
            work["derived_ethnicity"].eq(NON_HISPANIC) & work["derived_race"].eq(WHITE),
            2,
            0,
        ),
    ).astype(np.int8)
    black_n = int((focal_code == 1).sum())
    white_n = int((focal_code == 2).sum())
    if black_n == 0 or white_n == 0:
        raise ValueError("Both focal cohorts are required")
    observed_black = float(work.loc[focal_code == 1, "is_unique"].mean())
    observed_white = float(work.loc[focal_code == 2, "is_unique"].mean())
    observed_ratio = observed_black / observed_white

    tract_codes, _ = pd.factorize(work["census_tract"], sort=True)
    cell_codes, _ = pd.factorize(
        pd.MultiIndex.from_frame(work[["census_tract", "applicant_age", "applicant_sex"]]),
        sort=True,
    )
    order = np.argsort(tract_codes, kind="stable")
    tract_sorted = tract_codes[order]
    starts = np.r_[0, np.flatnonzero(np.diff(tract_sorted)) + 1]
    stops = np.r_[starts[1:], len(order)]
    tract_blocks = []
    for start, stop in zip(starts, stops, strict=True):
        indices = order[start:stop]
        _, local_cells = np.unique(cell_codes[indices], return_inverse=True)
        tract_blocks.append((local_cells.astype(np.int32), focal_code[indices].copy()))

    rng = np.random.Generator(np.random.PCG64(seed))
    ratios = np.empty(iterations, dtype=float)
    for iteration in range(iterations):
        unique_black = 0
        unique_white = 0
        for local_cells, labels in tract_blocks:
            shuffled = rng.permutation(labels)
            focal = shuffled > 0
            if not focal.any():
                continue
            combined = local_cells[focal] * 2 + (shuffled[focal] - 1)
            counts = np.bincount(combined)
            unique_black += int((counts[0::2] == 1).sum())
            unique_white += int((counts[1::2] == 1).sum())
        ratios[iteration] = (unique_black / black_n) / (unique_white / white_n)

    null_mean = float(ratios.mean())
    p_value = float(
        (1 + np.count_nonzero(np.abs(ratios - null_mean) >= abs(observed_ratio - null_mean)))
        / (iterations + 1)
    )
    return PermutationResult(
        observed_ratio=float(observed_ratio),
        null_mean=null_mean,
        null_std=float(ratios.std(ddof=1)),
        null_ci_low=float(np.quantile(ratios, 0.025)),
        null_ci_high=float(np.quantile(ratios, 0.975)),
        p_value_two_sided=p_value,
        iterations=iterations,
        seed=seed,
    )
