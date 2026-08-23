from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class AdjustedDisparityResult:
    status: str
    record_count: int
    reference_n: int
    comparison_n: int
    reference_denial_rate: float | None
    comparison_denial_rate: float | None
    adjusted_log_odds_coefficient: float | None
    adjusted_odds_ratio: float | None
    odds_ratio_ci_low: float | None
    odds_ratio_ci_high: float | None
    approximate_average_marginal_effect_points: float | None
    common_support_reference_share: float | None
    common_support_comparison_share: float | None
    converged: bool
    iterations: int

    def to_dict(self) -> dict[str, str | int | float | bool | None]:
        return asdict(self)


def _design_matrix(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    required = {"is_black", "is_denied", "protected_income", "protected_loan_amount"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing adjusted-model fields: {missing}")

    continuous = pd.DataFrame(index=frame.index)
    for field in ("protected_income", "protected_loan_amount"):
        values = pd.to_numeric(frame[field], errors="coerce").clip(lower=0)
        transformed = np.log1p(values)
        median = float(transformed.median()) if transformed.notna().any() else 0.0
        transformed = transformed.fillna(median)
        scale = float(transformed.std(ddof=0))
        continuous[f"z_log_{field}"] = (transformed - transformed.mean()) / (scale or 1.0)

    categorical_fields = [
        "applicant_age",
        "applicant_sex",
        "protected_geography",
        "loan_type",
        "debt_to_income_ratio",
        "loan_purpose",
        "occupancy_type",
        "lien_status",
        "derived_dwelling_category",
    ]
    available = [field for field in categorical_fields if field in frame.columns]
    categories = frame[available].fillna("Missing").astype(str)
    categories = pd.get_dummies(categories, prefix=available, drop_first=True, dtype=float)

    predictors = pd.concat(
        [frame[["is_black"]].astype(float), continuous, categories], axis=1
    )
    predictors = predictors.loc[:, predictors.nunique(dropna=False) > 1]
    if "is_black" not in predictors:
        raise ValueError("Both race comparison groups must be present")
    names = ["intercept", *predictors.columns.tolist()]
    x = np.column_stack([np.ones(len(predictors)), predictors.to_numpy(dtype=float)])
    y = frame["is_denied"].to_numpy(dtype=float)
    return x, y, names


def adjusted_denial_disparity(
    frame: pd.DataFrame,
    *,
    max_iterations: int = 100,
    tolerance: float = 1e-8,
) -> AdjustedDisparityResult:
    """Fit an aggregate-safe adjusted logistic model with deterministic IRLS."""
    reference = frame.loc[frame["is_black"] == 0, "is_denied"]
    comparison = frame.loc[frame["is_black"] == 1, "is_denied"]
    support_fields = sorted(
        set(frame.columns)
        - {"is_black", "is_denied"}
    )
    support = frame[support_fields].fillna("<MISSING>").astype(str).copy()
    support["is_black"] = frame["is_black"].to_numpy()
    represented = support.groupby(support_fields, observed=True)["is_black"].transform("nunique")
    common = represented.eq(2)
    reference_support_share = float(common.loc[frame["is_black"].eq(0)].mean()) if len(reference) else None
    comparison_support_share = float(common.loc[frame["is_black"].eq(1)].mean()) if len(comparison) else None
    if len(reference) < 2 or len(comparison) < 2:
        return AdjustedDisparityResult(
            "insufficient_retained_comparison", len(frame), len(reference), len(comparison),
            float(reference.mean()) if len(reference) else None,
            float(comparison.mean()) if len(comparison) else None,
            None, None, None, None, None,
            reference_support_share, comparison_support_share, False, 0,
        )

    x, y, names = _design_matrix(frame)
    beta = np.zeros(x.shape[1])
    converged = False
    iteration = 0
    ridge = np.eye(x.shape[1]) * 1e-8
    ridge[0, 0] = 0
    for iteration in range(1, max_iterations + 1):
        eta = np.clip(x @ beta, -30, 30)
        probability = 1 / (1 + np.exp(-eta))
        weights = np.clip(probability * (1 - probability), 1e-9, None)
        hessian = (x.T * weights) @ x + ridge
        score = x.T @ (y - probability) - ridge @ beta
        step = np.linalg.pinv(hessian) @ score
        beta = beta + step
        if float(np.max(np.abs(step))) < tolerance:
            converged = True
            break

    probability = 1 / (1 + np.exp(-np.clip(x @ beta, -30, 30)))
    weights = np.clip(probability * (1 - probability), 1e-9, None)
    covariance = np.linalg.pinv((x.T * weights) @ x + ridge)
    race_index = names.index("is_black")
    coefficient = float(beta[race_index])
    standard_error = float(np.sqrt(max(covariance[race_index, race_index], 0)))
    safe_exp = lambda value: float(np.exp(np.clip(value, -700, 700)))
    return AdjustedDisparityResult(
        status="estimated" if converged else "maximum_iterations_reached",
        record_count=len(frame),
        reference_n=len(reference),
        comparison_n=len(comparison),
        reference_denial_rate=float(reference.mean()),
        comparison_denial_rate=float(comparison.mean()),
        adjusted_log_odds_coefficient=coefficient,
        adjusted_odds_ratio=safe_exp(coefficient),
        odds_ratio_ci_low=safe_exp(coefficient - 1.96 * standard_error),
        odds_ratio_ci_high=safe_exp(coefficient + 1.96 * standard_error),
        approximate_average_marginal_effect_points=float(
            100 * coefficient * np.mean(probability * (1 - probability))
        ),
        common_support_reference_share=reference_support_share,
        common_support_comparison_share=comparison_support_share,
        converged=converged,
        iterations=iteration,
    )
