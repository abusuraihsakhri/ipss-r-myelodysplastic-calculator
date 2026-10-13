"""Validation and audit-tampering regression tests."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.base import AuditTrail, SecurityException
from ipss_r import (
    calculate_metrics, classify_ipss_r, score_anc, score_blasts,
    score_hemoglobin, score_platelets,
)


@pytest.mark.parametrize(
    "scorer",
    [score_blasts, score_hemoglobin, score_platelets, score_anc],
)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), "", None])
def test_invalid_numeric_rejected(scorer, value):
    with pytest.raises(ValueError):
        scorer(value)


def test_blast_range_is_percentage():
    assert score_blasts(100) == 3
    with pytest.raises(ValueError, match="exceed"):
        score_blasts(100.01)


@pytest.mark.parametrize("field", ["blast_pct", "hemoglobin", "platelets", "anc"])
def test_invalid_case_field_rejected(field):
    parameters = {
        "cytogenetic_risk": "good", "blast_pct": 3,
        "hemoglobin": 9, "platelets": 80, "anc": 1.2
    }
    parameters[field] = math.nan
    with pytest.raises(ValueError):
        calculate_metrics(**parameters)


@pytest.mark.parametrize("score", [math.nan, math.inf, -1, 10.5])
def test_invalid_classification_rejected(score):
    with pytest.raises(ValueError):
        classify_ipss_r(score)


def test_audit_verification_recalculates_hmac_and_returns_copy():
    audit = AuditTrail(secret_key="test-secret-32-characters-012345")
    audit.log("tester", "reviewer", "CHECK", {"status": "OK"})
    audit.log("tester", "reviewer", "SECOND", {"status": "OK"})
    assert audit.verify_integrity() is True

    exposed = audit.get_trail()
    exposed[0]["event_type"] = "FORGED"
    assert audit.verify_integrity() is True

    audit.logs[0]["event_type"] = "FORGED"
    assert audit.verify_integrity() is False


def test_no_implicit_audit_secret(monkeypatch):
    monkeypatch.delenv("AUDIT_SECRET_KEY", raising=False)
    with pytest.raises(SecurityException, match="required"):
        AuditTrail()
