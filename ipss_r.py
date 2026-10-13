#!/usr/bin/env python3
"""
Revised IPSS (IPSS-R) for Myelodysplastic Syndromes
Calculates IPSS-R prognostic score for MDS based on cytogenetics, blasts, hemoglobin, platelets, and ANC.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT

IPSS-R Scoring (Greenberg et al., 2012):
- Cytogenetic risk: 0-4 points
- Bone marrow blasts: 0-3 points
- Hemoglobin: 0-1.5 points
- Platelets: 0-1 point
- ANC: 0-0.5 points

Risk Categories:
- Very Low: <=1.5
- Low: >1.5-3
- Intermediate: >3-4.5
- High: >4.5-6
- Very High: >6
"""

import argparse
import csv
import json
import math
import sys
from typing import Dict, Any, List, Optional, Tuple


# IPSS-R Cytogenetic risk categories (simplified representation)
CYTOGENETIC_RISK_SCORES = {
    "very_good": 0,   # del(11q), -Y
    "good": 1,        # normal, del(5q), del(12p), del(20q), double including del(5q)
    "intermediate": 2,  # del(7q), +8, +19, i(17q), other single/double
    "poor": 3,        # -7, inv(3)/t(3q)/del(3q), double including -7/del(7q), complex (3)
    "very_poor": 4,   # complex (>3 abnormalities)
}


def _nonnegative_finite(value: float, label: str, maximum: Optional[float] = None) -> float:
    """Validate numbers before applying prognostic scoring cutoffs."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite number")
    if number < 0:
        raise ValueError(f"{label} cannot be negative")
    if maximum is not None and number > maximum:
        raise ValueError(f"{label} cannot exceed {maximum:g}")
    return number


def score_cytogenetics(cytogenetic_risk: str) -> float:
    """Score cytogenetic risk category (0-4 points)."""
    risk = str(cytogenetic_risk).strip().lower().replace(" ", "_").replace("-", "_")
    if risk in ("very_good", "verygood", "vg"):
        return 0.0
    elif risk in ("good", "g"):
        return 1.0
    elif risk in ("intermediate", "int", "i"):
        return 2.0
    elif risk in ("poor", "p"):
        return 3.0
    elif risk in ("very_poor", "verypoor", "vp", "very_bad"):
        return 4.0
    else:
        raise ValueError(
            f"Unknown cytogenetic risk category: '{cytogenetic_risk}'. "
            f"Valid: very_good, good, intermediate, poor, very_poor"
        )


def score_blasts(blast_pct: float) -> float:
    """Score bone marrow blast percentage (0-3 points)."""
    pct = _nonnegative_finite(blast_pct, "Blast percentage", 100.0)
    if pct <= 2.0:
        return 0.0
    elif pct < 5.0:
        return 1.0
    elif pct <= 10.0:
        return 2.0
    else:
        return 3.0


def score_hemoglobin(hemoglobin: float) -> float:
    """Score hemoglobin level (0-1.5 points)."""
    hgb = _nonnegative_finite(hemoglobin, "Hemoglobin")
    if hgb >= 10.0:
        return 0.0
    elif hgb >= 8.0:
        return 1.0
    else:
        return 1.5


def score_platelets(platelets: float) -> float:
    """Score platelet count (0-1 point)."""
    plt = _nonnegative_finite(platelets, "Platelet count")
    if plt >= 100.0:
        return 0.0
    elif plt >= 50.0:
        return 0.5
    else:
        return 1.0


def score_anc(anc: float) -> float:
    """Score absolute neutrophil count (0-0.5 points)."""
    neutrophil = _nonnegative_finite(anc, "ANC")
    if neutrophil >= 0.8:
        return 0.0
    else:
        return 0.5


def classify_ipss_r(total_score: float) -> Tuple[str, str]:
    """Classify IPSS-R total score into risk category."""
    score = _nonnegative_finite(total_score, "IPSS-R score", 10.0)
    note = "Prognostic classification only; treatment requires individualized specialist assessment."
    if score <= 1.5:
        return "Very Low", note
    elif score <= 3.0:
        return "Low", note
    elif score <= 4.5:
        return "Intermediate", note
    elif score <= 6.0:
        return "High", note
    else:
        return "Very High", note


def calculate_metrics(
    cytogenetic_risk: str = None,
    blast_pct: float = None,
    hemoglobin: float = None,
    platelets: float = None,
    anc: float = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate IPSS-R prognostic score for Myelodysplastic Syndromes.

    Parameters:
        cytogenetic_risk: Cytogenetic risk category (very_good, good, intermediate, poor, very_poor)
        blast_pct: Bone marrow blast percentage (0-100)
        hemoglobin: Hemoglobin level (g/dL)
        platelets: Platelet count (x10^9/L)
        anc: Absolute neutrophil count (x10^9/L)

    Returns:
        Dictionary with IPSS-R score, classification, and component breakdown.
    """
    # Validate required parameters
    missing = []
    if cytogenetic_risk is None:
        missing.append("cytogenetic_risk")
    if blast_pct is None:
        missing.append("blast_pct")
    if hemoglobin is None:
        missing.append("hemoglobin")
    if platelets is None:
        missing.append("platelets")
    if anc is None:
        missing.append("anc")

    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    # Calculate component scores
    cyto_score = score_cytogenetics(cytogenetic_risk)
    blast_score = score_blasts(blast_pct)
    hgb_score = score_hemoglobin(hemoglobin)
    plt_score = score_platelets(platelets)
    anc_score = score_anc(anc)

    total_score = round(cyto_score + blast_score + hgb_score + plt_score + anc_score, 2)

    classification, recommendation = classify_ipss_r(total_score)

    return {
        "tool": "ipss-r-myelodysplastic-calculator",
        "ipss_r_score": total_score,
        "risk_category": classification,
        "clinical_recommendation": recommendation,
        "component_scores": {
            "cytogenetics": cyto_score,
            "bone_marrow_blasts": blast_score,
            "hemoglobin": hgb_score,
            "platelets": plt_score,
            "anc": anc_score,
        },
        "inputs": {
            "cytogenetic_risk": str(cytogenetic_risk),
            "blast_pct": float(blast_pct),
            "hemoglobin": float(hemoglobin),
            "platelets": float(platelets),
            "anc": float(anc),
        },
    }


def process_single(args) -> None:
    """Process a single IPSS-R evaluation from CLI args."""
    kwargs = vars(args)
    kwargs.pop("func", None)
    kwargs.pop("command", None)
    res = calculate_metrics(**kwargs)
    print(json.dumps(res, indent=2))


def process_batch(input_csv: str, output_csv: str) -> None:
    """
    Process batch IPSS-R evaluations from CSV.

    Expected CSV columns: cytogenetic_risk, blast_pct, hemoglobin, platelets, anc
    """
    import os
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, restkey="__extra_fields__")
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not fieldnames:
        raise ValueError("Input CSV must contain a header row")
    if any(not name or not name.strip() for name in fieldnames):
        raise ValueError("Input CSV contains a blank column name")
    if len(set(fieldnames)) != len(fieldnames):
        raise ValueError("Input CSV contains duplicate column names")

    # Map common column name variants
    column_mapping = {
        "cytogenetic_risk": ["cytogenetic_risk", "cytogenetics", "cyto_risk", "cytogenetic"],
        "blast_pct": ["blast_pct", "blasts", "blast_percentage", "bm_blasts"],
        "hemoglobin": ["hemoglobin", "hgb", "hb"],
        "platelets": ["platelets", "plt", "platelet_count"],
        "anc": ["anc", "absolute_neutrophil_count", "neutrophils"],
    }

    out_fields = list(dict.fromkeys(fieldnames + ["ipss_r_score", "risk_category", "clinical_recommendation"]))
    out_rows = []
    errors = []

    for idx, r in enumerate(rows):
        if "__extra_fields__" in r:
            message = "CSV record has more fields than the header"
            errors.append(f"Row {idx + 2}: {message}")
            row_dict = {name: r.get(name, "") for name in fieldnames}
            row_dict.update(ipss_r_score="ERROR", risk_category="ERROR", clinical_recommendation=message)
            out_rows.append(row_dict)
            continue

        # Normalize column names
        normalized = {}
        for target, alternatives in column_mapping.items():
            for alt in alternatives:
                if alt in r:
                    normalized[target] = r[alt]
                    break

        try:
            calc_res = calculate_metrics(**normalized)
            row_dict = {name: r.get(name, '') for name in fieldnames}
            row_dict["ipss_r_score"] = calc_res["ipss_r_score"]
            row_dict["risk_category"] = calc_res["risk_category"]
            row_dict["clinical_recommendation"] = calc_res["clinical_recommendation"]
            out_rows.append(row_dict)
        except (ValueError, TypeError) as e:
            errors.append(f"Row {idx + 2}: {e}")
            row_dict = dict(r)
            row_dict["ipss_r_score"] = "ERROR"
            row_dict["risk_category"] = "ERROR"
            row_dict["clinical_recommendation"] = str(e)
            out_rows.append(row_dict)

    with open(output_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {output_csv}")
    if errors:
        print(f"  {len(errors)} errors encountered:")
        for err in errors[:5]:
            print(f"    - {err}")
        if len(errors) > 5:
            print(f"    ... and {len(errors) - 5} more")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Revised IPSS (IPSS-R) for Myelodysplastic Syndromes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single evaluation
  python ipss_r.py single --cytogenetic_risk good --blast_pct 3.0 --hemoglobin 9.0 --platelets 80 --anc 1.2

  # Batch processing
  python ipss_r.py batch -i patients.csv -o results.csv

Cytogenetic Risk Categories:
  very_good, good, intermediate, poor, very_poor
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single parser
    single_parser = subparsers.add_parser("single", help="Evaluate single case")
    single_parser.add_argument(
        "--cytogenetic_risk", type=str, required=True,
        choices=["very_good", "good", "intermediate", "poor", "very_poor"],
        help="Cytogenetic risk category"
    )
    single_parser.add_argument("--blast_pct", type=float, required=True, help="Bone marrow blast percentage (0-100)")
    single_parser.add_argument("--hemoglobin", type=float, required=True, help="Hemoglobin level (g/dL)")
    single_parser.add_argument("--platelets", type=float, required=True, help="Platelet count (x10^9/L)")
    single_parser.add_argument("--anc", type=float, required=True, help="Absolute neutrophil count (x10^9/L)")
    single_parser.set_defaults(func=process_single)

    # Batch parser
    batch_parser = subparsers.add_parser("batch", help="Process batch CSV")
    batch_parser.add_argument("-i", "--input", required=True, help="Input CSV file")
    batch_parser.add_argument("-o", "--output", default="results.csv", help="Output CSV file")

    args = parser.parse_args(argv)

    if args.command == "single":
        args.func(args)
    elif args.command == "batch":
        process_batch(args.input, args.output)


if __name__ == "__main__":
    main()
