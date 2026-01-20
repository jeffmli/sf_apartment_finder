"""Configuration loader for apartment scraper."""
import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any

class Config:
    """Configuration manager for the apartment scraper."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration."""
        load_dotenv()

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Load environment variables
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')

    def get_search_criteria(self) -> Dict[str, Any]:
        """Get search criteria."""
        return self.config.get('search_criteria', {})

    def get_scraper_config(self, scraper_name: str) -> Dict[str, Any]:
        """Get configuration for a specific scraper."""
        return self.config.get('scrapers', {}).get(scraper_name, {})

    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration."""
        return self.config.get('email', {})

    def is_scraper_enabled(self, scraper_name: str) -> bool:
        """Check if a scraper is enabled."""
        return self.get_scraper_config(scraper_name).get('enabled', False)
