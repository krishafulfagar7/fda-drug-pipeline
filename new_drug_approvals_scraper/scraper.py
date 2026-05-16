"""
scraper.py
---------
Drop-in replacement that pulls data from the official OpenFDA Drugs@FDA API
instead of scraping Drugs.com.

API docs: https://open.fda.gov/apis/drug/drugsfda/
"""

import logging
import os
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

from .config import CONFIG, LocalConfig, AWSConfig, GCPConfig
from .load_data import (
    load_existing_data,
    export_data_to_local,
    export_data_to_s3,
    export_data_to_cloud_storage,
)
from new_drug_approvals_scraper.utils import initialize_model, clean_company_name
from new_drug_approvals_scraper.classification import (
    make_classification,
    DRUG_CATEGORIES,
    DRUG_DESCRIPTION,
    DRUG_CLASSIFICATION_TEMPLATE,
    DISEASE_CATEGORIES,
    DISEASE_DESCRIPTION,
    DISEASE_CLASSIFICATION_TEMPLATE,
)

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

FDA_API_BASE = "https://api.fda.gov/drug/drugsfda.json"
RESULTS_PER_PAGE = 99


def fetch_fda_approvals(start_year: int, end_year: int) -> list[dict]:
    all_records: list[dict] = []
    skip = 0

    date_from = f"{start_year}0101"
    date_to = f"{end_year}1231"

    logging.info(f"Fetching FDA approvals from {start_year} to {end_year}...")

    while True:
        params = {
            "search": "submissions.submission_status_date:[" + date_from + "+TO+" + date_to + "]",
            "limit": RESULTS_PER_PAGE,
            "skip": skip,
        }

        try:
            from urllib.parse import quote

            encoded_search = quote(
                "submissions.submission_status_date:[" + date_from + "+TO+" + date_to + "]",
                safe=":+[]",
            )
            url = (
                f"{FDA_API_BASE}?search={encoded_search}"
                f"&limit={RESULTS_PER_PAGE}&skip={skip}"
            )
            response = requests.get(url, timeout=30)
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            break

        if response.status_code == 404:
            break
        if response.status_code != 200:
            logging.error(f"FDA API error {response.status_code}: {response.text[:200]}")
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            break

        all_records.extend(results)
        total = data.get("meta", {}).get("results", {}).get("total", "?")
        logging.info(f"  Fetched {len(all_records)} / {total} records...")

        if len(results) < RESULTS_PER_PAGE:
            break

        skip += RESULTS_PER_PAGE
        time.sleep(0.5)  # be polite to the API

    return all_records


def _format_openfda_date(date_yyyymmdd: str) -> Optional[str]:
    if not date_yyyymmdd:
        return None
    try:
        dt = datetime.strptime(date_yyyymmdd, "%Y%m%d")
    except ValueError:
        return None
    return dt.strftime(CONFIG.DATE_FORMAT)


def parse_fda_record(record: dict) -> dict:
    app_number = record.get("application_number", "")

    sponsor = clean_company_name(record.get("sponsor_name", "") or "")

    products = record.get("products") or []
    first_product = products[0] if products else {}

    drug_name = (first_product.get("brand_name") or "").strip()

    active_ingredients = first_product.get("active_ingredients")
    generic_names: list[str] = []
    if isinstance(active_ingredients, list):
        for ing in active_ingredients:
            if isinstance(ing, dict):
                name = (ing.get("name") or "").strip()
                if name:
                    generic_names.append(name)
    drug_generic_name = ", ".join(generic_names) if generic_names else None

    dosage_form = (first_product.get("dosage_form") or "").strip()
    route = (first_product.get("route") or "").strip()
    mode_administration = " via ".join([p for p in [dosage_form, route] if p]) or None

    submissions = record.get("submissions") or []
    approved = [
        s
        for s in submissions
        if isinstance(s, dict) and (s.get("submission_status") or "").upper() == "AP"
    ]
    approved.sort(key=lambda s: s.get("submission_status_date", ""), reverse=True)
    latest = approved[0] if approved else {}

    approval_date_raw = latest.get("submission_status_date", "") if latest else ""
    approval_date = _format_openfda_date(approval_date_raw)

    submission_type = (latest.get("submission_type") or "").strip() if latest else ""
    marketing_status = (first_product.get("marketing_status") or "").strip()

    # The Drugs@FDA endpoint doesn't provide a clean "Treatment for" field like Drugs.com.
    treatment_for = None
    description = " | ".join([p for p in [submission_type, marketing_status] if p]) or ""

    return {
        "drug_name": drug_name,
        "drug_generic_name": drug_generic_name,
        "mode_administration": mode_administration,
        "description": description,
        "Date of Approval": approval_date,
        "Company": sponsor,
        "Treatment for": treatment_for,
        "application_number": app_number,
    }


def scrape_new_drug_approvals_data(openai_api_key: Optional[str] = None) -> None:
    if not openai_api_key:
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OpenAI API key not found. Please provide it as an argument or set OPENAI_API_KEY."
            )

    chat = initialize_model(openai_api_key)

    existing_result = load_existing_data()
    df_initial, _most_recent_year = (
        existing_result if existing_result else (pd.DataFrame(), None)
    )

    existing_apps = (
        set(df_initial["application_number"].dropna().astype(str).tolist())
        if not df_initial.empty and "application_number" in df_initial.columns
        else set()
    )

    start_year = 2023
    end_year = int(datetime.utcnow().year)

    raw_records = fetch_fda_approvals(start_year, end_year)
    logging.info(f"Total raw records fetched: {len(raw_records)}")

    parsed = [parse_fda_record(r) for r in raw_records]
    new_records = [
        r for r in parsed if str(r.get("application_number", "")) not in existing_apps
    ]
    logging.info(f"New records to classify: {len(new_records)}")

    if not new_records:
        logging.info("Nothing new to process. Exiting.")
        return

    enriched: list[dict] = []
    for record in tqdm(new_records, desc="Classifying drugs"):
        drug_name = record.get("drug_name")
        mode_administration = record.get("mode_administration")
        drug_description = record.get("description")
        drug_treatment = record.get("Treatment for")

        record["drug_type"] = make_classification(
            categories=DRUG_CATEGORIES,
            item_description=DRUG_DESCRIPTION,
            template=DRUG_CLASSIFICATION_TEMPLATE,
            chat=chat,
            drug_name=drug_name,
            mode_administration=mode_administration,
            drug_description=drug_description,
            drug_treatment=drug_treatment,
        )

        record["disease_type"] = make_classification(
            categories=DISEASE_CATEGORIES,
            item_description=DISEASE_DESCRIPTION,
            template=DISEASE_CLASSIFICATION_TEMPLATE,
            chat=chat,
            drug_name=drug_name,
            drug_treatment=drug_treatment,
        )

        enriched.append(record)
        time.sleep(0.2)  # slight pause between LLM calls

    df_new = pd.DataFrame(enriched)
    df_combined = (
        pd.concat([df_new, df_initial], ignore_index=True)
        if not df_initial.empty
        else df_new
    )

    if isinstance(CONFIG, LocalConfig):
        export_data_to_local(df_combined)
    elif isinstance(CONFIG, AWSConfig):
        export_data_to_s3(df_combined)
    elif isinstance(CONFIG, GCPConfig):
        export_data_to_cloud_storage(df_combined)
    else:
        raise RuntimeError(
            f"Invalid CONFIG detected. CONFIG must be an instance of either LocalConfig, AWSConfig, or GCPConfig. "
            f"Current CONFIG: {type(CONFIG).__name__}"
        )
