"""Zillow apartment scraper."""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
import time
import re
import json
from . import BaseScraper

logger = logging.getLogger(__name__)


class ZillowScraper(BaseScraper):
    """Scraper for Zillow apartment listings."""

    def __init__(self, search_criteria: Dict[str, Any], base_url: str = "https://www.zillow.com"):
        """Initialize Zillow scraper."""
        super().__init__(search_criteria)
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def _build_search_url(self) -> str:
        """Build Zillow search URL based on criteria."""
        # Format location for URL
        location = self.search_criteria.get('location', 'San Francisco, CA')
        location_slug = location.lower().replace(', ', '-').replace(' ', '-')

        # Base URL for rentals
        url = f"{self.base_url}/{location_slug}/rentals"

        # Build query parameters
        params = []

        # Price range
        min_price = self.search_criteria.get('min_price')
        max_price = self.search_criteria.get('max_price')
        if min_price or max_price:
            price_filter = f"{min_price or '0'}-{max_price or ''}_price"
            params.append(price_filter)

        # Bedrooms
        min_bedrooms = self.search_criteria.get('min_bedrooms')
        if min_bedrooms:
            params.append(f"{min_bedrooms}-_beds")

        # Join filters
        if params:
            url += "/" + "_".join(params)

        return url

    def _parse_price(self, price_text: str) -> int:
        """Extract numeric price from text."""
        if not price_text:
            return 0
        # Remove $ and commas, extract first number
        match = re.search(r'[\$]?([\d,]+)', price_text.replace('+', ''))
        if match:
            return int(match.group(1).replace(',', ''))
        return 0

    def _extract_json_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Try to extract listing data from JSON in page."""
        results = []

        try:
            # Zillow often embeds data in script tags
            script_tags = soup.find_all('script', type='application/json')

            for script in script_tags:
                try:
                    data = json.loads(script.string)

                    # Look for property data in various possible locations
                    if isinstance(data, dict):
                        # Try to find listings in the data structure
                        self._extract_listings_from_json(data, results)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.debug(f"Error parsing JSON from script tag: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error extracting JSON data: {e}")

        return results

    def _extract_listings_from_json(self, data: dict, results: List[Dict[str, Any]]):
        """Recursively extract listing data from JSON structure."""
        if isinstance(data, dict):
            # Check if this looks like a listing
            if 'price' in data and 'address' in data:
                listing = self._parse_json_listing(data)
                if listing:
                    results.append(listing)

            # Recurse through dictionary
            for value in data.values():
                if isinstance(value, (dict, list)):
                    self._extract_listings_from_json(value, results)

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_listings_from_json(item, results)

    def _parse_json_listing(self, data: dict) -> Dict[str, Any]:
        """Parse a single listing from JSON data."""
        try:
            price = data.get('price', 'N/A')
            if isinstance(price, (int, float)):
                price_value = int(price)
                price_text = f"${price_value:,}"
            else:
                price_text = str(price)
                price_value = self._parse_price(price_text)

            address = data.get('address', {})
            if isinstance(address, dict):
                location = address.get('streetAddress', 'N/A')
            else:
                location = str(address)

            return {
                'title': data.get('name', location),
                'price': price_value,
                'price_text': price_text,
                'bedrooms': data.get('bedrooms', 'N/A'),
                'bathrooms': data.get('bathrooms', 'N/A'),
                'sqft': data.get('livingArea', 'N/A'),
                'location': location,
                'url': data.get('url', 'N/A'),
                'source': 'Zillow',
                'date_posted': 'N/A'
            }
        except Exception as e:
            logger.debug(f"Error parsing JSON listing: {e}")
            return None

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape Zillow for apartment listings."""
        logger.info("Starting Zillow scrape...")
        self.results = []

        try:
            url = self._build_search_url()
            logger.info(f"Searching Zillow: {url}")

            # Add delay to be respectful
            time.sleep(2)

            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to extract from JSON first (more reliable)
            json_results = self._extract_json_data(soup)
            if json_results:
                self.results.extend(json_results[:self.search_criteria.get('max_results_per_site', 50)])
                logger.info(f"Found {len(self.results)} Zillow listings from JSON data")
                return self.results

            # Fallback: Try to parse HTML (may not work well due to dynamic content)
            logger.warning("Could not extract Zillow data from JSON, attempting HTML parse...")

            # Look for listing cards (structure may vary)
            listing_cards = soup.find_all('article', class_=re.compile(r'.*list-card.*'))

            if not listing_cards:
                listing_cards = soup.find_all('div', {'data-test': 'property-card'})

            max_results = self.search_criteria.get('max_results_per_site', 50)

            for card in listing_cards[:max_results]:
                try:
                    apartment = self._parse_html_listing(card)
                    if apartment:
                        self.results.append(apartment)
                except Exception as e:
                    logger.debug(f"Error parsing Zillow listing card: {e}")
                    continue

            logger.info(f"Found {len(self.results)} Zillow listings")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error scraping Zillow: {e}")
            logger.warning("Zillow may be blocking requests. Consider using a different approach or reducing request frequency.")
        except Exception as e:
            logger.error(f"Error scraping Zillow: {e}")

        return self.results

    def _parse_html_listing(self, card) -> Dict[str, Any]:
        """Parse a listing from HTML card element."""
        # Extract link
        link = card.find('a', class_=re.compile(r'.*list-card-link.*'))
        url = link.get('href', 'N/A') if link else 'N/A'
        if url != 'N/A' and not url.startswith('http'):
            url = self.base_url + url

        # Extract price
        price_elem = card.find('div', class_=re.compile(r'.*list-card-price.*'))
        price_text = price_elem.text.strip() if price_elem else "N/A"
        price = self._parse_price(price_text)

        # Extract address
        address_elem = card.find('address')
        location = address_elem.text.strip() if address_elem else "N/A"

        # Extract info (beds/baths/sqft)
        info_elem = card.find('ul', class_=re.compile(r'.*list-card-details.*'))
        bedrooms = 'N/A'
        bathrooms = 'N/A'
        sqft = 'N/A'

        if info_elem:
            info_text = info_elem.text
            bed_match = re.search(r'(\d+)\s*bd', info_text)
            bath_match = re.search(r'(\d+)\s*ba', info_text)
            sqft_match = re.search(r'([\d,]+)\s*sqft', info_text)

            if bed_match:
                bedrooms = bed_match.group(1)
            if bath_match:
                bathrooms = bath_match.group(1)
            if sqft_match:
                sqft = sqft_match.group(1).replace(',', '')

        return {
            'title': location,
            'price': price,
            'price_text': price_text,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'sqft': sqft,
            'location': location,
            'url': url,
            'source': 'Zillow',
            'date_posted': 'N/A'
        }
