import pandas as pd

from hmda_privacy.config import QIConfig
from hmda_privacy.diversity import equivalence_class_diversity, summarize_diversity


def test_l_diversity_and_t_closeness_are_aggregate() -> None:
    frame = pd.DataFrame(
        {
            "tract": ["1", "1", "2", "2"],
            "denied": [0, 1, 0, 0],
        }
    )
    config = QIConfig(1, "test", ("tract",), (), ("denied",), 2, (1, 5, 10))
    classes = equivalence_class_diversity(frame, config, sensitive_attribute="denied")
    assert set(classes) == {"tract", "k", "l_distinct", "t_total_variation"}
    assert classes.set_index("tract").loc["1", "l_distinct"] == 2
    summary = summarize_diversity(classes, l_threshold=2, t_threshold=0.2)
    assert summary["records_failing_l_diversity"] == 2
    assert summary["records_failing_t_closeness"] == 4

