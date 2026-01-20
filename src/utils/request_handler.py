"""Request utilities with anti-detection features."""
import requests
import random
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SmartRequestHandler:
    """Handle requests with anti-detection measures."""

    # Rotate through multiple user agents to appear more like different browsers
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    def __init__(self, base_delay: float = 3.0, max_retries: int = 3):
        """Initialize request handler."""
        self.base_delay = base_delay
        self.max_retries = max_retries
        self.session = requests.Session()

    def get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """Generate realistic browser headers."""
        headers = {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        if referer:
            headers['Referer'] = referer

        return headers

    def get_with_retry(
        self,
        url: str,
        referer: Optional[str] = None,
        timeout: int = 30
    ) -> Optional[requests.Response]:
        """Make GET request with retries and anti-detection."""
        for attempt in range(self.max_retries):
            try:
                # Add random delay before request
                delay = self.base_delay + random.uniform(0, 2)
                if attempt > 0:
                    # Exponential backoff on retries
                    delay = delay * (2 ** attempt)

                logger.debug(f"Waiting {delay:.1f}s before request (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(delay)

                # Get fresh headers for each request
                headers = self.get_headers(referer=referer)

                # Make request
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True
                )

                # Check response status
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    logger.warning(f"403 Forbidden (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        continue
                    else:
                        response.raise_for_status()
                elif response.status_code == 429:
                    logger.warning(f"429 Too Many Requests (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        # Longer delay for rate limiting
                        time.sleep(10 * (2 ** attempt))
                        continue
                    else:
                        response.raise_for_status()
                else:
                    response.raise_for_status()

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error: {e} (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise

        return None

    def close(self):
        """Close the session."""
        self.session.close()
