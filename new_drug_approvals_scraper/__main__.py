import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="new_drug_approvals_scraper",
        description="Scrape and classify new drug approvals data.",
    )
    parser.add_argument(
        "--openai-api-key",
        dest="openai_api_key",
        default=None,
        help="OpenAI API key (defaults to OPENAI_API_KEY env var).",
    )
    args = parser.parse_args()

    # Import lazily so `--help` works without optional deps installed.
    from .scraper import scrape_new_drug_approvals_data
    scrape_new_drug_approvals_data(openai_api_key=args.openai_api_key)


if __name__ == "__main__":
    main()
