import pytest
from playwright.sync_api import Page, Browser, BrowserContext
from config.settings import settings

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Pass headless setting from .env to the browser launcher."""
    return {
        **browser_type_launch_args,
        "headless": settings.HEADLESS,
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": "videos/",
        "record_video_size": {"width": 1280, "height": 720},
    }

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """Create a new page for each test."""
    page = context.new_page()
    page.set_default_timeout(settings.TIMEOUT)
    yield page
    # Cleanup
    page.close()