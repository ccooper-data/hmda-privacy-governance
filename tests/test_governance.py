from datetime import UTC, date, datetime, timedelta

import pytest

from hmda_privacy.governance import validate_governance_policy, validate_retention


def policy():
    return {
        "allowed_classifications": ["public", "internal", "quasi_identifier", "sensitive"],
        "restricted_in_published_marts": ["internal"],
        "published_marts": {"risk": {"columns": {"count": "public", "secret": "internal"}}},
    }


def test_unclassified_and_restricted_columns_fail() -> None:
    violations = validate_governance_policy(policy(), {"risk": ["count", "secret", "new"]})
    assert {item.code for item in violations} == {
        "RESTRICTED_PUBLICATION",
        "UNCLASSIFIED_COLUMN",
    }


def test_active_time_bounded_exception_is_honored() -> None:
    exceptions = {
        "exceptions": [
            {
                "id": "EX-1",
                "code": "RESTRICTED_PUBLICATION",
                "model": "risk",
                "column": "secret",
                "owner": "privacy-officer",
                "reason": "test",
                "expires_on": "2026-09-01",
            }
        ]
    }
    violations = validate_governance_policy(
        policy(), {"risk": ["count", "secret"]}, exceptions=exceptions, as_of=date(2026, 8, 22)
    )
    assert violations == []


def test_retention_requires_aware_timestamps() -> None:
    now = datetime(2026, 8, 22, tzinfo=UTC)
    assert validate_retention(created_at=now - timedelta(days=5), retention_days=10, as_of=now)
    assert not validate_retention(created_at=now - timedelta(days=11), retention_days=10, as_of=now)
    with pytest.raises(ValueError, match="timezone-aware"):
        validate_retention(
            created_at=datetime(2026, 8, 1),  # noqa: DTZ001 - intentionally naive
            retention_days=10,
            as_of=now,
        )
