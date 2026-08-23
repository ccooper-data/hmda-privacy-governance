from pathlib import Path

from hmda_privacy.reporting import build_release_figures

if __name__ == "__main__":
    outputs = build_release_figures(
        Path("docs/results/texas_2023_summary.json"), Path("docs/figures")
    )
    for output in outputs:
        print(output)
