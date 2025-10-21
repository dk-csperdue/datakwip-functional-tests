"""DataKwip UI client with Playwright automation."""

from typing import Any, Dict, List, Optional
from pathlib import Path

from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext


class UITestError(Exception):
    """UI test error."""

    pass


class DataKwipUIClient:
    """Client for DataKwip UI automation using Playwright."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        headless: bool = True,
        browser_type: str = "chromium",
        timeout: int = 60000,
        screenshot_dir: Optional[str] = None,
    ):
        """Initialize UI client.

        Args:
            base_url: Base URL of DataKwip UI
            username: User email/username
            password: User password
            headless: Run browser in headless mode
            browser_type: Browser type (chromium, firefox, webkit)
            timeout: Default timeout in milliseconds
            screenshot_dir: Directory to save screenshots on failure
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.headless = headless
        self.browser_type = browser_type
        self.timeout = timeout
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else None

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def start(self):
        """Start Playwright and browser."""
        self._playwright = sync_playwright().start()

        # Get browser launcher
        if self.browser_type == "chromium":
            launcher = self._playwright.chromium
        elif self.browser_type == "firefox":
            launcher = self._playwright.firefox
        elif self.browser_type == "webkit":
            launcher = self._playwright.webkit
        else:
            raise ValueError(f"Invalid browser type: {self.browser_type}")

        # Launch browser
        self._browser = launcher.launch(headless=self.headless)

        # Create context with reasonable viewport
        self._context = self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,  # Allow self-signed certs in dev
        )

        # Set default timeout
        self._context.set_default_timeout(self.timeout)

        # Create page
        self._page = self._context.new_page()

    def _save_screenshot(self, name: str):
        """Save screenshot on failure."""
        if self.screenshot_dir and self._page:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = self.screenshot_dir / f"{name}.png"
            self._page.screenshot(path=str(screenshot_path))
            print(f"Screenshot saved: {screenshot_path}")

    def login(self) -> bool:
        """Login to DataKwip UI via Keycloak.

        Returns:
            True if login successful

        Raises:
            UITestError: On login failure
        """
        if not self._page:
            raise UITestError("Browser not started. Call start() first.")

        try:
            # Navigate to home page
            self._page.goto(self.base_url)

            # Wait for redirect to Keycloak login page
            self._page.wait_for_url("**/realms/datakwip/protocol/openid-connect/**", timeout=10000)

            # Fill login form
            self._page.fill('input[name="username"]', self.username)
            self._page.fill('input[name="password"]', self.password)

            # Submit form
            self._page.click('input[type="submit"]')

            # Wait for redirect back to app
            self._page.wait_for_url(f"{self.base_url}/**", timeout=10000)

            # Verify we're logged in (check for logout button or user menu)
            # This depends on your UI structure
            try:
                self._page.wait_for_selector('[data-testid="user-menu"]', timeout=5000)
            except:
                # Fallback: check if we're not on login page
                current_url = self._page.url
                if "realms/datakwip" in current_url:
                    raise UITestError("Still on login page after submission")

            return True

        except Exception as e:
            self._save_screenshot("login_failure")
            raise UITestError(f"Login failed: {str(e)}")

    def navigate_to_data_explorer(self) -> bool:
        """Navigate to Data Explorer page.

        Returns:
            True if navigation successful

        Raises:
            UITestError: On navigation failure
        """
        if not self._page:
            raise UITestError("Browser not started. Call start() first.")

        try:
            # Click on Data Explorer link/button
            # Adjust selector based on your UI structure
            self._page.click('a[href*="data-explorer"], a:has-text("Data Explorer")')

            # Wait for page load
            self._page.wait_for_load_state("networkidle")

            # Verify we're on the right page
            current_url = self._page.url
            if "data-explorer" not in current_url.lower():
                raise UITestError(f"Not on Data Explorer page: {current_url}")

            return True

        except Exception as e:
            self._save_screenshot("navigation_failure")
            raise UITestError(f"Navigation failed: {str(e)}")

    def execute_query(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Execute a query in Data Explorer.

        Args:
            query: Optional query string (if None, uses default/first available)

        Returns:
            Query results metadata

        Raises:
            UITestError: On query execution failure
        """
        if not self._page:
            raise UITestError("Browser not started. Call start() first.")

        try:
            if query:
                # Fill query input
                self._page.fill('textarea[name="query"], input[name="query"]', query)

            # Click execute/run button
            self._page.click('button:has-text("Execute"), button:has-text("Run")')

            # Wait for results to load
            self._page.wait_for_selector('[data-testid="query-results"]', timeout=15000)

            # Extract results count or other metadata
            # Adjust selectors based on your UI structure
            results_text = self._page.text_content('[data-testid="results-count"]')

            return {
                "success": True,
                "results_summary": results_text,
                "url": self._page.url,
            }

        except Exception as e:
            self._save_screenshot("query_failure")
            raise UITestError(f"Query execution failed: {str(e)}")

    def get_page_title(self) -> str:
        """Get current page title."""
        if not self._page:
            raise UITestError("Browser not started. Call start() first.")
        return self._page.title()

    def get_current_url(self) -> str:
        """Get current URL."""
        if not self._page:
            raise UITestError("Browser not started. Call start() first.")
        return self._page.url

    def close(self):
        """Close browser and Playwright."""
        if self._page:
            self._page.close()
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
