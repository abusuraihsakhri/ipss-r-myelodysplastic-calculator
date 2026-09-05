"""
Tests for IPSS-R Myelodysplastic Calculator core functionality.
"""
import pytest
from ipss_r import (
    calculate_metrics,
    process_batch,
    score_cytogenetics,
    score_blasts,
    score_hemoglobin,
    score_platelets,
    score_anc,
    classify_ipss_r,
)


class TestCytogeneticsScoring:
    def test_very_good(self):
        assert score_cytogenetics("very_good") == 0.0
        assert score_cytogenetics("verygood") == 0.0
        assert score_cytogenetics("VG") == 0.0

    def test_good(self):
        assert score_cytogenetics("good") == 1.0
        assert score_cytogenetics("G") == 1.0

    def test_intermediate(self):
        assert score_cytogenetics("intermediate") == 2.0
        assert score_cytogenetics("int") == 2.0

    def test_poor(self):
        assert score_cytogenetics("poor") == 3.0
        assert score_cytogenetics("P") == 3.0

    def test_very_poor(self):
        assert score_cytogenetics("very_poor") == 4.0
        assert score_cytogenetics("verypoor") == 4.0
        assert score_cytogenetics("VP") == 4.0

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown cytogenetic risk"):
            score_cytogenetics("invalid")


class TestBlastsScoring:
    def test_low_blasts(self):
        assert score_blasts(0) == 0.0
        assert score_blasts(1.5) == 0.0
        assert score_blasts(2.0) == 0.0

    def test_moderate_blasts(self):
        assert score_blasts(2.1) == 1.0
        assert score_blasts(4.9) == 1.0

    def test_high_blasts(self):
        assert score_blasts(5.0) == 2.0
        assert score_blasts(10.0) == 2.0

    def test_very_high_blasts(self):
        assert score_blasts(10.1) == 3.0
        assert score_blasts(20.0) == 3.0

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            score_blasts(-1.0)


class TestHemoglobinScoring:
    def test_normal(self):
        assert score_hemoglobin(10.0) == 0.0
        assert score_hemoglobin(15.0) == 0.0

    def test_moderate_anemia(self):
        assert score_hemoglobin(8.0) == 1.0
        assert score_hemoglobin(9.5) == 1.0

    def test_severe_anemia(self):
        assert score_hemoglobin(7.9) == 1.5
        assert score_hemoglobin(5.0) == 1.5

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            score_hemoglobin(-1.0)


class TestPlateletsScoring:
    def test_normal(self):
        assert score_platelets(100.0) == 0.0
        assert score_platelets(200.0) == 0.0

    def test_moderate_thrombocytopenia(self):
        assert score_platelets(50.0) == 0.5
        assert score_platelets(75.0) == 0.5

    def test_severe_thrombocytopenia(self):
        assert score_platelets(49.9) == 1.0
        assert score_platelets(10.0) == 1.0

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            score_platelets(-1.0)


class TestANCScoring:
    def test_normal(self):
        assert score_anc(0.8) == 0.0
        assert score_anc(2.0) == 0.0

    def test_low(self):
        assert score_anc(0.79) == 0.5
        assert score_anc(0.1) == 0.5

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            score_anc(-1.0)


class TestClassification:
    def test_very_low(self):
        cat, _ = classify_ipss_r(0.0)
        assert cat == "Very Low"
        cat, _ = classify_ipss_r(1.5)
        assert cat == "Very Low"

    def test_low(self):
        cat, _ = classify_ipss_r(1.6)
        assert cat == "Low"
        cat, _ = classify_ipss_r(3.0)
        assert cat == "Low"

    def test_intermediate(self):
        cat, _ = classify_ipss_r(3.1)
        assert cat == "Intermediate"
        cat, _ = classify_ipss_r(4.5)
        assert cat == "Intermediate"

    def test_high(self):
        cat, _ = classify_ipss_r(4.6)
        assert cat == "High"
        cat, _ = classify_ipss_r(6.0)
        assert cat == "High"

    def test_very_high(self):
        cat, _ = classify_ipss_r(6.1)
        assert cat == "Very High"
        cat, _ = classify_ipss_r(10.0)
        assert cat == "Very High"


class TestCalculateMetrics:
    def test_complete_calculation(self):
        res = calculate_metrics(
            cytogenetic_risk="good",
            blast_pct=3.0,
            hemoglobin=9.0,
            platelets=80,
            anc=1.2,
        )
        # good=1.0, blasts 3%=1.0, hgb 9=1.0, platelets 80=0.5, anc 1.2=0.0
        assert res["ipss_r_score"] == 3.5
        assert res["risk_category"] == "Intermediate"
        assert "clinical_recommendation" in res
        assert "component_scores" in res

    def test_very_low_risk(self):
        res = calculate_metrics(
            cytogenetic_risk="very_good",
            blast_pct=1.0,
            hemoglobin=12.0,
            platelets=150,
            anc=2.0,
        )
        assert res["ipss_r_score"] == 0.0
        assert res["risk_category"] == "Very Low"

    def test_very_high_risk(self):
        res = calculate_metrics(
            cytogenetic_risk="very_poor",
            blast_pct=15.0,
            hemoglobin=6.0,
            platelets=20,
            anc=0.3,
        )
        assert res["ipss_r_score"] == 10.0  # 4 + 3 + 1.5 + 1 + 0.5
        assert res["risk_category"] == "Very High"

    def test_missing_params_raises(self):
        with pytest.raises(ValueError, match="Missing required parameters"):
            calculate_metrics(cytogenetic_risk="good")

    def test_returns_component_breakdown(self):
        res = calculate_metrics(
            cytogenetic_risk="intermediate",
            blast_pct=5.0,
            hemoglobin=8.5,
            platelets=60,
            anc=0.5,
        )
        components = res["component_scores"]
        assert components["cytogenetics"] == 2.0
        assert components["bone_marrow_blasts"] == 2.0
        assert components["hemoglobin"] == 1.0
        assert components["platelets"] == 0.5
        assert components["anc"] == 0.5


class TestBatchProcessing:
    def test_batch_processing(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "Patient_ID,cytogenetic_risk,blast_pct,hemoglobin,platelets,anc\n"
            "PT-001,good,3.0,9.0,80,1.2\n"
            "PT-002,intermediate,7.0,7.5,45,0.6\n",
            encoding="utf-8",
        )

        process_batch(str(csv_in), str(csv_out))
        assert csv_out.exists()
        content = csv_out.read_text(encoding="utf-8")
        assert "PT-001" in content
        assert "ipss_r_score" in content
        assert "risk_category" in content

    def test_batch_with_errors(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "Patient_ID,cytogenetic_risk,blast_pct,hemoglobin,platelets,anc\n"
            "PT-001,invalid,3.0,9.0,80,1.2\n",
            encoding="utf-8",
        )

        process_batch(str(csv_in), str(csv_out))
        assert csv_out.exists()
        content = csv_out.read_text(encoding="utf-8")
        assert "ERROR" in content

    def test_batch_missing_file(self, tmp_path):
        csv_in = tmp_path / "nonexistent.csv"
        csv_out = tmp_path / "out.csv"

        with pytest.raises(FileNotFoundError):
            process_batch(str(csv_in), str(csv_out))
