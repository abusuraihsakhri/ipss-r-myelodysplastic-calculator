"""API-level scoring regression tests without a network dependency."""
import sys
from pathlib import Path
import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.api import CalculationRequest, api_calculate, homepage


def test_api_matches_published_case():
    result = api_calculate(CalculationRequest(
        cytogenetic_risk="good",
        blast_pct=3, hemoglobin=9, platelets=80, anc=1.2
    ))
    assert result["ipss_r_score"] == 3.5
    assert result["risk_category"] == "Intermediate"


def test_api_rejects_out_of_range_blasts():
    with pytest.raises(HTTPException) as exc:
        api_calculate(CalculationRequest(
            cytogenetic_risk="good",
            blast_pct=101, hemoglobin=9, platelets=80, anc=1.2
        ))
    assert exc.value.status_code == 422


def test_local_homepage_is_present():
    result = homepage()
    assert Path(result.path).is_file()
    assert Path(result.path).name == "index.html"
