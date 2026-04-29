# Playwright Automation Project

A state-of-the-art Playwright test automation framework built with Python for production environments.

## Features

- **Parallel Execution**: Run tests across multiple workers for faster execution
- **Cross-Browser Testing**: Support for Chromium, Firefox, and WebKit
- **Rich Reporting**: Allure and HTML reports with screenshots and videos
- **Page Object Model**: Modular and maintainable test structure
- **CI/CD Ready**: GitHub Actions workflow for automated testing
- **Environment Configuration**: Flexible settings via environment variables

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd automation-playwright
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install --with-deps
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Running Tests

- **Run all tests**: `pytest`
- **Run with specific browser**: `pytest --browser=firefox`
- **Run in headed mode**: `pytest --headed`
- **Generate reports**: Reports are automatically generated in `reports/`

## Project Structure

```
├── tests/              # Test files
│   └── conftest.py     # Pytest fixtures
├── pages/              # Page object models
│   └── base_page.py    # Base page class
├── utils/              # Utility functions
├── config/             # Configuration files
│   └── settings.py     # Application settings
├── reports/            # Generated reports
├── data/               # Test data files
├── screenshots/        # Failure screenshots
├── videos/             # Test recordings
└── scripts/            # Setup and utility scripts
```

## CI/CD

Tests run automatically on push and pull requests via GitHub Actions. Results are uploaded as artifacts.