import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""

    # Timeouts
    TIMEOUT = int(os.getenv("TIMEOUT", 30000))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", 60000))
    SHORT_TIMEOUT = int(os.getenv("SHORT_TIMEOUT", 5000))

    # URLs
    BASE_URL = os.getenv("BASE_URL", "https://drivejoulez.com")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://beta.drivejoulez.com:8443/joulez-service")

    # Browser settings
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER = os.getenv("BROWSER", "chromium")

    # Parallel settings
    WORKERS = int(os.getenv("WORKERS", 4))

    # Reporting
    ALLURE_DIR = os.getenv("ALLURE_DIR", "reports/allure-results")
    HTML_REPORT_DIR = os.getenv("HTML_REPORT_DIR", "reports/html")

settings = Settings()