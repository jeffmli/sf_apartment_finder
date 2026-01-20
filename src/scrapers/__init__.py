"""Apartment scrapers."""
from typing import List, Dict, Any

class BaseScraper:
    """Base class for apartment scrapers."""

    def __init__(self, search_criteria: Dict[str, Any]):
        """Initialize scraper with search criteria."""
        self.search_criteria = search_criteria
        self.results = []

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape apartments. To be implemented by subclasses."""
        raise NotImplementedError

    def get_results(self) -> List[Dict[str, Any]]:
        """Get scraping results."""
        return self.results
