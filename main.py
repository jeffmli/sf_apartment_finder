#!/usr/bin/env python3
"""
Main script for SF Apartment Finder.
Scrapes apartment listings from multiple sources and emails results.
"""
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any

from src.config_loader import Config
from src.scrapers.craigslist_scraper import CraigslistScraper
from src.scrapers.zillow_scraper import ZillowScraper
from src.scrapers.apartments_scraper import ApartmentsScraper
from src.utils.spreadsheet_generator import SpreadsheetGenerator
from src.utils.email_sender import EmailSender


def setup_logging():
    """Configure logging."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)

    # File handler
    log_filename = f'logs/scraper_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def scrape_all_sites(config: Config) -> List[Dict[str, Any]]:
    """Scrape all enabled apartment sites."""
    logger = logging.getLogger(__name__)
    all_listings = []
    search_criteria = config.get_search_criteria()

    logger.info("=" * 80)
    logger.info("Starting apartment search...")
    logger.info(f"Location: {search_criteria.get('location')}")
    logger.info(f"Price range: ${search_criteria.get('min_price')} - ${search_criteria.get('max_price')}")
    logger.info(f"Bedrooms: {search_criteria.get('min_bedrooms')} - {search_criteria.get('max_bedrooms')}")
    logger.info("=" * 80)

    # Craigslist
    if config.is_scraper_enabled('craigslist'):
        try:
            logger.info("\n--- Scraping Craigslist ---")
            scraper_config = config.get_scraper_config('craigslist')
            scraper = CraigslistScraper(
                search_criteria=search_criteria,
                base_url=scraper_config.get('base_url')
            )
            listings = scraper.scrape()
            all_listings.extend(listings)
            logger.info(f"Craigslist: Found {len(listings)} listings")
        except Exception as e:
            logger.error(f"Error scraping Craigslist: {e}")

    # Zillow
    if config.is_scraper_enabled('zillow'):
        try:
            logger.info("\n--- Scraping Zillow ---")
            scraper_config = config.get_scraper_config('zillow')
            scraper = ZillowScraper(
                search_criteria=search_criteria,
                base_url=scraper_config.get('base_url')
            )
            listings = scraper.scrape()
            all_listings.extend(listings)
            logger.info(f"Zillow: Found {len(listings)} listings")
        except Exception as e:
            logger.error(f"Error scraping Zillow: {e}")

    # Apartments.com
    if config.is_scraper_enabled('apartments_com'):
        try:
            logger.info("\n--- Scraping Apartments.com ---")
            scraper_config = config.get_scraper_config('apartments_com')
            scraper = ApartmentsScraper(
                search_criteria=search_criteria,
                base_url=scraper_config.get('base_url')
            )
            listings = scraper.scrape()
            all_listings.extend(listings)
            logger.info(f"Apartments.com: Found {len(listings)} listings")
        except Exception as e:
            logger.error(f"Error scraping Apartments.com: {e}")

    logger.info("=" * 80)
    logger.info(f"Total listings found: {len(all_listings)}")
    logger.info("=" * 80)

    return all_listings


def main():
    """Main execution function."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("🏠 SF Apartment Finder Starting...")

        # Load configuration
        config = Config()

        # Validate email configuration
        if not config.sender_email or not config.sender_password:
            logger.error("Email credentials not configured! Please set SENDER_EMAIL and SENDER_PASSWORD in .env file")
            sys.exit(1)

        if not config.recipient_email:
            logger.error("Recipient email not configured! Please set RECIPIENT_EMAIL in .env file")
            sys.exit(1)

        # Scrape all sites
        listings = scrape_all_sites(config)

        if not listings:
            logger.warning("No listings found. Email will not be sent.")
            return

        # Generate spreadsheet
        logger.info("\nGenerating spreadsheet...")
        spreadsheet_gen = SpreadsheetGenerator()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = spreadsheet_gen.generate_csv(listings, f"apartments_{timestamp}.csv")

        # Get summary statistics
        stats = spreadsheet_gen.get_summary_stats(listings)

        # Send email
        logger.info("\nSending email...")
        email_sender = EmailSender(
            sender_email=config.sender_email,
            sender_password=config.sender_password
        )

        email_config = config.get_email_config()
        subject = email_config.get('subject', 'Daily Apartment Listings').format(
            date=datetime.now().strftime("%B %d, %Y")
        )

        success = email_sender.send_apartment_email(
            recipient_email=config.recipient_email,
            listings=listings,
            attachment_path=csv_path,
            subject=subject,
            stats=stats
        )

        if success:
            logger.info("✅ Apartment search completed successfully!")
        else:
            logger.error("❌ Failed to send email")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
