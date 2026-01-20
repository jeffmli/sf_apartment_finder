"""Apartments.com apartment scraper."""
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
import re
import json
from . import BaseScraper
from ..utils.request_handler import SmartRequestHandler

logger = logging.getLogger(__name__)


class ApartmentsScraper(BaseScraper):
    """Scraper for Apartments.com listings."""

    def __init__(self, search_criteria: Dict[str, Any], base_url: str = "https://www.apartments.com"):
        """Initialize Apartments.com scraper."""
        super().__init__(search_criteria)
        self.base_url = base_url.rstrip('/')
        self.request_handler = SmartRequestHandler(base_delay=4.0, max_retries=3)

    def _build_search_url(self) -> str:
        """Build Apartments.com search URL based on criteria."""
        # Format location for URL
        location = self.search_criteria.get('location', 'San Francisco, CA')
        location_slug = location.lower().replace(', ', '-').replace(' ', '-')

        # Base URL
        url = f"{self.base_url}/{location_slug}/"

        # Build query parameters
        params = []

        # Price range
        min_price = self.search_criteria.get('min_price')
        max_price = self.search_criteria.get('max_price')

        if min_price:
            params.append(f"min-price={min_price}")
        if max_price:
            params.append(f"max-price={max_price}")

        # Bedrooms
        min_bedrooms = self.search_criteria.get('min_bedrooms')
        max_bedrooms = self.search_criteria.get('max_bedrooms')

        if min_bedrooms:
            params.append(f"min-beds={min_bedrooms}")
        if max_bedrooms:
            params.append(f"max-beds={max_bedrooms}")

        # Bathrooms
        min_bathrooms = self.search_criteria.get('min_bathrooms')
        if min_bathrooms:
            params.append(f"min-baths={min_bathrooms}")

        # Join parameters
        if params:
            url += "?" + "&".join(params)

        return url

    def _parse_price(self, price_text: str) -> int:
        """Extract numeric price from text."""
        if not price_text or price_text == 'N/A':
            return 0

        # Handle price ranges (e.g., "$2,000 - $3,000")
        if '-' in price_text:
            # Take the minimum price from range
            price_text = price_text.split('-')[0].strip()

        # Extract number
        match = re.search(r'[\$]?([\d,]+)', price_text)
        if match:
            return int(match.group(1).replace(',', ''))
        return 0

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape Apartments.com for apartment listings."""
        logger.info("Starting Apartments.com scrape...")
        self.results = []

        try:
            url = self._build_search_url()
            logger.info(f"Searching Apartments.com: {url}")

            # Use smart request handler with retries
            response = self.request_handler.get_with_retry(
                url,
                referer="https://www.google.com/",
                timeout=30
            )

            if not response:
                logger.error("Failed to fetch Apartments.com page after all retries")
                return self.results

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to find JSON data first
            json_results = self._extract_json_data(soup)
            if json_results:
                self.results.extend(json_results[:self.search_criteria.get('max_results_per_site', 50)])
                logger.info(f"Found {len(self.results)} Apartments.com listings from JSON")
                return self.results

            # Parse HTML listings
            # Apartments.com uses different class names, try multiple selectors
            listings = soup.find_all('article', class_=re.compile(r'.*placard.*'))

            if not listings:
                listings = soup.find_all('li', class_=re.compile(r'.*mortar-wrapper.*'))

            if not listings:
                listings = soup.find_all('div', {'data-testid': 'property-card'})

            max_results = self.search_criteria.get('max_results_per_site', 50)
            count = 0

            for listing in listings:
                if count >= max_results:
                    break

                try:
                    apartment = self._parse_html_listing(listing)
                    if apartment:
                        self.results.append(apartment)
                        count += 1
                except Exception as e:
                    logger.debug(f"Error parsing Apartments.com listing: {e}")
                    continue

            logger.info(f"Found {len(self.results)} Apartments.com listings")

        except Exception as e:
            logger.error(f"Error scraping Apartments.com: {e}")
            logger.warning("Apartments.com may be blocking requests. This is common with their anti-scraping measures.")
        finally:
            self.request_handler.close()

        return self.results

    def _extract_json_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Try to extract listing data from JSON in page."""
        results = []

        try:
            # Look for JSON-LD structured data
            script_tags = soup.find_all('script', type='application/ld+json')

            for script in script_tags:
                try:
                    data = json.loads(script.string)

                    # Handle both single objects and arrays
                    items = data if isinstance(data, list) else [data]

                    for item in items:
                        if isinstance(item, dict) and item.get('@type') == 'ApartmentComplex':
                            # This is a property listing
                            listing = self._parse_json_listing(item)
                            if listing:
                                results.append(listing)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.debug(f"Error parsing JSON-LD: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error extracting JSON data: {e}")

        return results

    def _parse_json_listing(self, data: dict) -> Dict[str, Any]:
        """Parse a single listing from JSON-LD data."""
        try:
            name = data.get('name', 'N/A')
            address_data = data.get('address', {})

            if isinstance(address_data, dict):
                street = address_data.get('streetAddress', '')
                city = address_data.get('addressLocality', '')
                location = f"{street}, {city}".strip(', ')
            else:
                location = 'N/A'

            # Price might be in offers
            price_text = 'N/A'
            price_value = 0

            offers = data.get('offers')
            if offers:
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                if isinstance(offers, dict):
                    price = offers.get('price')
                    if price:
                        price_value = int(float(price))
                        price_text = f"${price_value:,}"

            url = data.get('url', 'N/A')
            if url != 'N/A' and not url.startswith('http'):
                url = self.base_url + url

            return {
                'title': name,
                'price': price_value,
                'price_text': price_text,
                'bedrooms': 'N/A',
                'bathrooms': 'N/A',
                'sqft': 'N/A',
                'location': location,
                'url': url,
                'source': 'Apartments.com',
                'date_posted': 'N/A'
            }

        except Exception as e:
            logger.debug(f"Error parsing JSON listing: {e}")
            return None

    def _parse_html_listing(self, listing) -> Dict[str, Any]:
        """Parse a single listing from HTML."""
        try:
            # Title/Property name
            title_elem = listing.find('span', class_=re.compile(r'.*js-placardTitle.*'))
            if not title_elem:
                title_elem = listing.find('a', class_=re.compile(r'.*property-link.*'))

            title = title_elem.text.strip() if title_elem else 'N/A'

            # URL
            link_elem = listing.find('a', class_=re.compile(r'.*property-link.*'))
            if not link_elem:
                link_elem = listing.find('a', href=re.compile(r'.*/[a-z-]+/\d+.*'))

            url = link_elem.get('href', 'N/A') if link_elem else 'N/A'
            if url != 'N/A' and not url.startswith('http'):
                url = self.base_url + url

            # Price
            price_elem = listing.find('p', class_=re.compile(r'.*property-pricing.*'))
            if not price_elem:
                price_elem = listing.find('p', class_=re.compile(r'.*price.*'))
            if not price_elem:
                price_elem = listing.find('span', class_=re.compile(r'.*price.*'))

            price_text = price_elem.text.strip() if price_elem else 'N/A'
            price = self._parse_price(price_text)

            # Location/Address
            location_elem = listing.find('div', class_=re.compile(r'.*property-address.*'))
            if not location_elem:
                location_elem = listing.find('div', class_=re.compile(r'.*location.*'))

            location = location_elem.text.strip() if location_elem else 'N/A'

            # Beds/Baths/SqFt
            bedrooms = 'N/A'
            bathrooms = 'N/A'
            sqft = 'N/A'

            # Look for property info
            info_elem = listing.find('p', class_=re.compile(r'.*property-beds.*'))
            if info_elem:
                info_text = info_elem.text
                bed_match = re.search(r'(\d+)\s*(?:Bed|bd)', info_text, re.IGNORECASE)
                bath_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:Bath|ba)', info_text, re.IGNORECASE)
                sqft_match = re.search(r'([\d,]+)\s*(?:Sq|sq)', info_text, re.IGNORECASE)

                if bed_match:
                    bedrooms = bed_match.group(1)
                if bath_match:
                    bathrooms = bath_match.group(1)
                if sqft_match:
                    sqft = sqft_match.group(1).replace(',', '')

            return {
                'title': title,
                'price': price,
                'price_text': price_text,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'sqft': sqft,
                'location': location,
                'url': url,
                'source': 'Apartments.com',
                'date_posted': 'N/A'
            }

        except Exception as e:
            logger.debug(f"Error parsing HTML listing: {e}")
            return None
