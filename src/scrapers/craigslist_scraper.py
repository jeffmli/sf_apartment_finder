"""Craigslist apartment scraper."""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
import time
import re
from . import BaseScraper

logger = logging.getLogger(__name__)


class CraigslistScraper(BaseScraper):
    """Scraper for Craigslist apartment listings."""

    def __init__(self, search_criteria: Dict[str, Any], base_url: str = "https://sfbay.craigslist.org"):
        """Initialize Craigslist scraper."""
        super().__init__(search_criteria)
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def _build_search_url(self) -> str:
        """Build Craigslist search URL based on criteria."""
        # Base search path for housing
        url = f"{self.base_url}/search/apa"

        # Build query parameters
        params = []

        # Price range
        min_price = self.search_criteria.get('min_price')
        max_price = self.search_criteria.get('max_price')
        if min_price:
            params.append(f"min_price={min_price}")
        if max_price:
            params.append(f"max_price={max_price}")

        # Bedrooms
        min_bedrooms = self.search_criteria.get('min_bedrooms')
        max_bedrooms = self.search_criteria.get('max_bedrooms')
        if min_bedrooms:
            params.append(f"min_bedrooms={min_bedrooms}")
        if max_bedrooms:
            params.append(f"max_bedrooms={max_bedrooms}")

        # Bathrooms
        min_bathrooms = self.search_criteria.get('min_bathrooms')
        if min_bathrooms:
            params.append(f"min_bathrooms={min_bathrooms}")

        # Features
        if self.search_criteria.get('pet_friendly'):
            params.append("pets_cat=1")
            params.append("pets_dog=1")

        if self.search_criteria.get('parking'):
            params.append("parking=1")

        if self.search_criteria.get('in_unit_laundry'):
            params.append("laundry=1")

        # Combine URL
        if params:
            url += "?" + "&".join(params)

        return url

    def _parse_price(self, price_text: str) -> int:
        """Extract numeric price from text."""
        if not price_text:
            return 0
        match = re.search(r'\$?([\d,]+)', price_text)
        if match:
            return int(match.group(1).replace(',', ''))
        return 0

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape Craigslist for apartment listings."""
        logger.info("Starting Craigslist scrape...")
        self.results = []

        try:
            url = self._build_search_url()
            logger.info(f"Searching Craigslist: {url}")

            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all listing items
            listings = soup.find_all('li', class_='cl-search-result')

            max_results = self.search_criteria.get('max_results_per_site', 50)
            count = 0

            for listing in listings:
                if count >= max_results:
                    break

                try:
                    # Extract listing data
                    title_elem = listing.find('div', class_='title')
                    if not title_elem:
                        continue

                    link_elem = title_elem.find('a')
                    if not link_elem:
                        continue

                    title = link_elem.text.strip()
                    url = link_elem.get('href', '')

                    # Make sure URL is absolute
                    if url and not url.startswith('http'):
                        url = self.base_url + url

                    # Price
                    price_elem = listing.find('div', class_='price')
                    price_text = price_elem.text.strip() if price_elem else "N/A"
                    price = self._parse_price(price_text)

                    # Location
                    location_elem = listing.find('div', class_='location')
                    location = location_elem.text.strip() if location_elem else "N/A"

                    # Housing info (bedrooms/bathrooms)
                    housing_elem = listing.find('div', class_='housing')
                    housing_text = housing_elem.text.strip() if housing_elem else ""

                    # Extract bedrooms
                    bedrooms = "N/A"
                    br_match = re.search(r'(\d+)br', housing_text)
                    if br_match:
                        bedrooms = br_match.group(1)

                    # Extract square footage
                    sqft = "N/A"
                    sqft_match = re.search(r'(\d+)ft', housing_text)
                    if sqft_match:
                        sqft = sqft_match.group(1)

                    # Date posted
                    date_elem = listing.find('div', class_='date')
                    date_posted = date_elem.get('title', 'N/A') if date_elem else "N/A"

                    apartment = {
                        'title': title,
                        'price': price,
                        'price_text': price_text,
                        'bedrooms': bedrooms,
                        'bathrooms': 'N/A',
                        'sqft': sqft,
                        'location': location,
                        'url': url,
                        'source': 'Craigslist',
                        'date_posted': date_posted
                    }

                    self.results.append(apartment)
                    count += 1

                except Exception as e:
                    logger.warning(f"Error parsing Craigslist listing: {e}")
                    continue

            logger.info(f"Found {len(self.results)} Craigslist listings")

        except Exception as e:
            logger.error(f"Error scraping Craigslist: {e}")

        return self.results
