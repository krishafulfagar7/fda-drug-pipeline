# FDA Drug Approval Intelligence Pipeline

> End-to-end data pipeline fetching, classifying, and visualizing FDA drug approval records — built as a work sample for RTW Institute's Data Analyst Internship.

---

## What This Does

This project pulls drug approval data directly from the **official openFDA API** — the same source cited in RTW Institute's research — classifies each drug using a large language model, and visualizes the results in an interactive dashboard.

| Stage | What happens |
|---|---|
| **Fetch** | Queries `api.fda.gov/drug/drugsfda.json` for all approval submissions |
| **Clean** | Parses sponsor names, active ingredients, dosage forms, approval dates |
| **Classify** | LLaMA 3.3 70B tags each drug by therapeutic type and disease area |
| **Visualize** | Streamlit dashboard with filters, trend charts, and a disease × drug matrix |

---

## Key Findings (2023–2026 Data)

- **9,998 records fetched** from openFDA · **2,550 fully classified** (API rate limit on free tier — pipeline is resumable)
- **Small molecules dominate** at 52% of classified drugs, but biologics, monoclonal antibodies, and RNA therapies show meaningful growth
- **Psychiatry, Infectious Disease, and Cardiovascular** are the top three disease areas — reflecting both high generic filing volume and sustained post-COVID pipeline activity
- **Approval volume grew** from 512 records in 2023 to 912 in 2025, with 2026 on pace to match
- **565 unique sponsor companies** — top 10 account for a disproportionate share, consistent with pharma consolidation trends

---

## Why It's Relevant to RTW Institute

RTW Institute focuses on two areas — **drug innovation incentives** and **healthcare affordability**. This pipeline directly supports both:

- Tracking novel approvals (NDA/BLA) vs. generics (ANDA) shows whether innovation incentives are translating into new treatments
- Monitoring approval volume by therapeutic modality (small molecule vs. biologic) informs policy discussions around different regulatory pathways
- Integrating CMS NADAC pricing data (planned next step) would enable direct drug cost analysis alongside approval trends

---

## Dashboard

Built with Streamlit + Plotly. Features:
- Year range filter (sidebar)
- Drug type filter
- Approvals over time (area chart)
- Drug type breakdown (donut chart)
- Approvals by disease area (bar chart)
- Top 10 companies by approvals
- Disease area × drug type heatmap

**Run locally:**
```bash
pip install streamlit plotly pandas
streamlit run streamlit_app.py
```

---

## Repo Structure

```
fda-drug-pipeline/
├── new_drug_approvals_scraper/   # Core scraper package (openFDA API)
├── data/
│   ├── new_drug_approvals.csv    # Raw fetched records (~10k rows)
│   └── clean_approvals.csv       # Classified subset (2,550 rows)
├── streamlit_app.py              # Interactive dashboard
├── fill_classifications.py       # LLM classification script (Groq API)
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Component | Tool |
|---|---|
| Data source | openFDA Drug Applications API |
| Data processing | Python · pandas |
| LLM classification | LLaMA 3.3 70B via Groq API |
| Dashboard | Streamlit · Plotly |
| Language | Python 3.14 |

---

## Limitations & Next Steps

Classification was completed on 2,550 of 9,998 records due to Groq's free-tier daily token limit (100k tokens/day). The pipeline tracks already-classified records and resumes where it left off — full classification would take ~2 hours with production API access.

Planned extensions:
- CMS NADAC pricing integration for affordability analysis
- NDA vs. ANDA vs. BLA breakdown
- Full historical dataset back to 2002
- Public dashboard deployment

---

*Data: openFDA Drug Applications API · Classification: LLaMA 3.3 70B via Groq · Built May 2026*
