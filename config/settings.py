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
    BASE_URL = os.getenv("BASE_URL", "https://revflow-dev.axgsolutions.com")

    # Auth (RevFlow uses Microsoft Azure AD SSO)
    AUTH_USERNAME = os.getenv("AUTH_USERNAME", "")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "")

    # Browser settings
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER = os.getenv("BROWSER", "chromium")

    # Parallel settings
    WORKERS = int(os.getenv("WORKERS", 1))

    # Reporting
    ALLURE_DIR = os.getenv("ALLURE_DIR", "reports/allure-results")
    HTML_REPORT_DIR = os.getenv("HTML_REPORT_DIR", "reports/html")
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "reports/screenshots")
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

settings = Settings()