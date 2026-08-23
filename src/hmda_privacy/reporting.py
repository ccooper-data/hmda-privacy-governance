from __future__ import annotations

import html
import json
from pathlib import Path


def _svg_line_chart(
    *, title: str, subtitle: str, series: list[tuple[str, str, list[float]]], x_labels: list[str]
) -> str:
    width, height = 900, 520
    left, right, top, bottom = 90, 35, 85, 80
    plot_w, plot_h = width - left - right, height - top - bottom
    maximum = max(value for _, _, values in series for value in values) * 1.12
    maximum = max(maximum, 0.01)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="34" font-family="Arial" font-size="24" font-weight="700" fill="#172033">{html.escape(title)}</text>',
        f'<text x="{left}" y="59" font-family="Arial" font-size="14" fill="#556070">{html.escape(subtitle)}</text>',
    ]
    for tick in range(6):
        value = maximum * tick / 5
        y = top + plot_h - plot_h * tick / 5
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#e5e9f0"/>'
        )
        parts.append(
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#556070">{100 * value:.0f}%</text>'
        )
    for index, label in enumerate(x_labels):
        x = left + plot_w * index / max(len(x_labels) - 1, 1)
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 28}" text-anchor="middle" font-family="Arial" font-size="12" fill="#384152">{html.escape(label)}</text>'
        )
    for series_index, (name, color, values) in enumerate(series):
        points = []
        for index, value in enumerate(values):
            x = left + plot_w * index / max(len(values) - 1, 1)
            y = top + plot_h - plot_h * value / maximum
            points.append(f"{x:.1f},{y:.1f}")
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>')
        parts.append(
            f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="3"/>'
        )
        legend_x = left + series_index * 245
        parts.append(
            f'<rect x="{legend_x}" y="{height - 28}" width="16" height="4" fill="{color}"/>'
        )
        parts.append(
            f'<text x="{legend_x + 24}" y="{height - 20}" font-family="Arial" font-size="13" fill="#384152">{html.escape(name)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_release_figures(summary_path: Path, output_dir: Path) -> list[Path]:
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    frontier = [
        row
        for row in data["frontier"]
        if row.get("minimum_detectable_disparity_points") is not None
    ]
    density = data["residential_density"]
    frontier_path = output_dir / "privacy_utility_frontier.svg"
    frontier_path.write_text(
        _svg_line_chart(
            title="Texas 2023 privacy–utility frontier",
            subtitle="Pre-suppression risk, retained share, and decision MDE by release state",
            x_labels=[
                row["configuration"].replace("_", " ")
                + (" (current)" if row["is_current_baseline"] else "")
                for row in frontier
            ],
            series=[
                (
                    "Pre-suppression uniqueness",
                    "#c43d4d",
                    [row["pre_suppression_uniqueness_rate"] for row in frontier],
                ),
                ("Records retained", "#237a57", [row["retained_share"] for row in frontier]),
                (
                    "MDE (percentage points)",
                    "#3478bf",
                    [row["minimum_detectable_disparity_points"] / 100 for row in frontier],
                ),
            ],
        ),
        encoding="utf-8",
    )
    density_by_quintile: dict[int, dict[tuple[str, str], float]] = {}
    for row in density:
        density_by_quintile.setdefault(row["residential_density_quintile"], {})[
            (row["derived_race"], row["derived_ethnicity"])
        ] = row["sample_uniqueness_rate"]
    quintiles = sorted(density_by_quintile)
    density_path = output_dir / "residential_density_risk.svg"
    density_path.write_text(
        _svg_line_chart(
            title="Uniqueness by residential-density quintile",
            subtitle="Black non-Hispanic risk is U-shaped; quintile 1 is lowest density",
            x_labels=[str(quintile) for quintile in quintiles],
            series=[
                ("Overall", "#44546a", [density_by_quintile[q][("ALL", "ALL")] for q in quintiles]),
                (
                    "Black non-Hispanic",
                    "#c43d4d",
                    [
                        density_by_quintile[q][
                            ("Black or African American", "Not Hispanic or Latino")
                        ]
                        for q in quintiles
                    ],
                ),
                (
                    "White non-Hispanic",
                    "#3478bf",
                    [
                        density_by_quintile[q][("White", "Not Hispanic or Latino")]
                        for q in quintiles
                    ],
                ),
            ],
        ),
        encoding="utf-8",
    )
    return [frontier_path, density_path]
