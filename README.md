# IPSS-R Myelodysplastic Calculator

A calculator for the **original Revised International Prognostic Scoring System (IPSS-R)** in myelodysplastic syndromes (MDS). It reports the total score (0–10), one of five prognostic categories, and individual point contributions.

## Browser calculator

The `web/` directory contains a responsive, standalone HTML/JavaScript calculator. Enter a cytogenetic risk group, bone marrow blast percentage, hemoglobin, platelets, and absolute neutrophil count (ANC); then select **Calculate IPSS-R**.

- All calculations execute locally in the browser, with **no network request, account, cookies, or local storage** required.
- Numerical fields reject missing, nonfinite, negative and out-of-range blast values.
- The browser edition needs no backend or Python runtime and can be opened from `web/index.html` or served as a static site.
- Cytogenetic risk grouping must first be determined from the full published karyotype definitions; the app does not infer groups from raw karyotypes.
- For research/batch use, the Python calculator below is the reference implementation.

## Score definitions

| Variable | Thresholds → score |
| --- | --- |
| Cytogenetics | Very good 0; Good 1; Intermediate 2; Poor 3; Very poor 4 |
| BM blasts (%) | ≤2: 0; >2 to <5: 1; 5–10: 2; >10: 3 |
| Hemoglobin (g/dL) | ≥10: 0; 8 to <10: 1; <8: 1.5 |
| Platelets (×10⁹/L) | ≥100: 0; 50 to <100: 0.5; <50: 1 |
| ANC (×10⁹/L) | ≥0.8: 0; <0.8: 0.5 |

| Total score | Prognostic risk |
| --- | --- |
| ≤1.5 | Very Low |
| >1.5 to 3 | Low |
| >3 to 4.5 | Intermediate |
| >4.5 to 6 | High |
| >6 | Very High |

**Scientific source:** Greenberg PL et al. *Revised International Prognostic Scoring System for Myelodysplastic Syndromes*. *Blood*. 2012;120:2454–2465. [doi:10.1182/blood-2012-03-420489](https://doi.org/10.1182/blood-2012-03-420489). See the [MDS Foundation / IWG-PM scoring tables](https://ipssradvanced.mds-foundation.org/).

## Python and REST API

Python 3.10+ is required for the server and the optional audit framework. The core `ipss_r.py` calculator uses only the Python standard library.

```bash
python -m pip install -r requirements.txt
python ipss_r.py single --cytogenetic_risk good --blast_pct 3 --hemoglobin 9 --platelets 80 --anc 1.2
python ipss_r.py batch -i sample.csv -o results.csv
python cli.py serve --host 127.0.0.1 --port 8000
```

The local browser UI will be available at `http://127.0.0.1:8000/`; interactive API documentation at `http://127.0.0.1:8000/docs`. Call `POST /api/calculate` with:

```json
{
  "cytogenetic_risk": "good",
  "blast_pct": 3,
  "hemoglobin": 9,
  "platelets": 80,
  "anc": 1.2
}
```

For batch CSV, required headers are `cytogenetic_risk,blast_pct,hemoglobin,platelets,anc`. Rows that fail validation are marked `ERROR`. The existing `cli.py audit`, `verify-audit`, `chat`, and `batch` commands operate on a **separate generic audit workflow**, not the IPSS-R clinical score.

The generic audit workflow uses an in-memory HMAC-SHA256 chain and requires a real secret supplied as `AUDIT_SECRET_KEY` (minimum 16 characters). Generate one with `python -c "import secrets; print(secrets.token_hex(32))"`; do not put production secrets in source, browser code, or Git history.

Docker: copy `.env.example` to `.env`, set a strong `AUDIT_SECRET_KEY`, and run `docker compose up --build`. The server listens on port 8000. The audit trail is in-memory, not durable storage.

## Tests

```bash
python -m pytest -q
node --test tests/test_browser_score.cjs
```

The CI workflow runs Python tests on 3.10–3.13 plus Node 22 browser-score and page-syntax tests. The Pages workflow publishes the static `web/` directory after merges to `master`.

## Privacy, scope, limitations

The **static browser calculator** transmits and stores no inputs. However, the optional API, generic audit framework, and local server have **not** been assessed as HIPAA-compliant; do not submit patient identifiers or protected health information to an exposed instance. Pattern-based identifier checks are not comprehensive de-identification or a security guarantee.

IPSS-R is a prognostic classification derived largely from untreated adult MDS cohorts; it is not a treatment rule, a diagnostic test, an IPSS-M implementation, a clinical decision support validation, or regulatory certification. It does not adjust estimates for age or molecular profiles. Clinical interpretation requires appropriate diagnostic and specialist review.

This project retains optional experimental generic audit, mock-chat, and enrichment modules. They do **not** implement or validate FHIR ingestion, cross-institutional analytics, or medical regulatory compliance.

**License:** [MIT](LICENSE). **Author:** Dr. Abu Suraih Sakhri.
