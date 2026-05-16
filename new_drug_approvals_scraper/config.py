from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path.cwd() / ".env"
load_dotenv(dotenv_path=env_path)
ENV = os.getenv("ENV", "local")


# Only for if you want to access to your Cloud Storage from Local
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'spacexploration-gcp-bucket-access.json' or None


class BaseConfig:
    SCRIPT_NAME = 'new_drug_approvals_scraper'
    DATE_FORMAT = '%B %d, %Y'
    BASE_YEAR = 2002
    LLM_MODEL = 'gpt-4o-mini'
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.drugs.com/",
        "Cache-Control": "max-age=0",
    }
    BASE_URL = 'https://www.drugs.com/newdrugs-archive'
    DATA_EXPORT_FILENAME = "new_drug_approvals.csv"


class LocalConfig(BaseConfig):
    DATA_DIR_NAME = 'data'


class AWSConfig(BaseConfig):
    BUCKET_NAME = "app-new-drug-approvals-bucket"


class GCPConfig(BaseConfig):
    BUCKET_NAME = 'new-drug-approvals-bucket'


def get_config():
    if ENV == "local":
        return LocalConfig()
    elif ENV == 'aws':
        return AWSConfig()
    elif ENV == 'gcp':
        return GCPConfig()
    return LocalConfig()


CONFIG = get_config()
