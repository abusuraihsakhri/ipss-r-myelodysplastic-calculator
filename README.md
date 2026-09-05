# IPSS-R Myelodysplastic Calculator

> **Domain:** Medical Oncology & Cancer Staging Systems  
> **Reference:** Greenberg et al., 2012 (Blood) - Revised IPSS for MDS

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)

</div>

---

## Overview

Revised International Prognostic Scoring System (IPSS-R) for Myelodysplastic Syndromes (MDS). Calculates prognostic scores based on cytogenetics, bone marrow blasts, hemoglobin, platelets, and ANC.

**Author:** Dr. Abu Suraih Sakhri  
**License:** MIT

---

## IPSS-R Scoring System

| Parameter | Range | Points |
|-----------|-------|--------|
| **Cytogenetics** | Very Good / Good / Intermediate / Poor / Very Poor | 0-4 |
| **Bone Marrow Blasts** | ≤2% / 2-5% / 5-10% / >10% | 0-3 |
| **Hemoglobin** | ≥10 / 8-10 / <8 g/dL | 0-1.5 |
| **Platelets** | ≥100 / 50-100 / <50 ×10⁹/L | 0-1 |
| **ANC** | ≥0.8 / <0.8 ×10⁹/L | 0-0.5 |

**Risk Categories:**
| Score | Category |
|-------|----------|
| ≤1.5 | Very Low |
| 1.5-3 | Low |
| 3-4.5 | Intermediate |
| 4.5-6 | High |
| >6 | Very High |

---

## Installation

```bash
# Clone repository
git clone https://github.com/abusuraihsakhri/ipss-r-myelodysplastic-calculator.git
cd ipss-r-myelodysplastic-calculator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set audit secret key (required for HMAC audit trail)
export AUDIT_SECRET_KEY="your-secure-key-here"  # Windows: set AUDIT_SECRET_KEY=...
```

---

## Usage

### Single Evaluation
```bash
python ipss_r.py single \
  --cytogenetic_risk good \
  --blast_pct 3.0 \
  --hemoglobin 9.0 \
  --platelets 80 \
  --anc 1.2
```

### Batch Processing
```bash
python ipss_r.py batch -i sample.csv -o results.csv
```

### Input CSV Format
| Column | Description | Unit |
|--------|-------------|------|
| `cytogenetic_risk` | Risk category | very_good/good/intermediate/poor/very_poor |
| `blast_pct` | Bone marrow blasts | % (0-100) |
| `hemoglobin` | Hemoglobin level | g/dL |
| `platelets` | Platelet count | ×10⁹/L |
| `anc` | Absolute neutrophil count | ×10⁹/L |

### FastAPI Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

---

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=. --cov-report=html
```

---

## Security

- **Audit Trail:** HMAC-SHA256 tamper-evident logging
- **Environment Variables:** `AUDIT_SECRET_KEY` must be set (min 16 chars)
- **No Hardcoded Secrets:** All sensitive values loaded from environment

---

## Docker Deployment

```bash
# Create .env file
cp .env.example .env
# Edit .env and set AUDIT_SECRET_KEY

# Build and run
docker compose up -d
```

---

## Project Structure

```
ipss-r-myelodysplastic-calculator/
├── ipss_r.py              # Core IPSS-R calculation engine
├── cli.py                 # CLI interface with FastAPI server
├── sample.csv             # Sample patient data
├── requirements.txt       # Python dependencies
├── agents/                # Enterprise supervisor framework
│   ├── base.py           # Security, PHI guard, audit trail
│   ├── models.py         # Pydantic data models
│   ├── supervisor.py     # Multi-worker orchestrator
│   ├── workers.py        # Specialized evaluation workers
│   └── api.py            # FastAPI REST endpoints
├── tests/                # Test suite
├── web/                  # Operations dashboard
└── Dockerfile            # Container configuration
```
