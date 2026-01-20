"""Spreadsheet generation utilities."""
import pandas as pd
from typing import List, Dict, Any
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class SpreadsheetGenerator:
    """Generate spreadsheets from apartment listings."""

    def __init__(self, output_dir: str = "output"):
        """Initialize spreadsheet generator."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_csv(self, listings: List[Dict[str, Any]], filename: str = None) -> str:
        """Generate CSV file from listings."""
        if not listings:
            logger.warning("No listings to generate CSV")
            return None

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"apartments_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        try:
            # Convert to DataFrame
            df = pd.DataFrame(listings)

            # Reorder columns for better readability
            column_order = [
                'source', 'title', 'price', 'price_text', 'bedrooms',
                'bathrooms', 'sqft', 'location', 'url', 'date_posted'
            ]

            # Only include columns that exist
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]

            # Sort by price (ascending)
            if 'price' in df.columns:
                df = df.sort_values('price', ascending=True)

            # Save to CSV
            df.to_csv(filepath, index=False, encoding='utf-8')

            logger.info(f"Generated CSV: {filepath} ({len(listings)} listings)")
            return filepath

        except Exception as e:
            logger.error(f"Error generating CSV: {e}")
            return None

    def generate_excel(self, listings: List[Dict[str, Any]], filename: str = None) -> str:
        """Generate Excel file from listings."""
        if not listings:
            logger.warning("No listings to generate Excel file")
            return None

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"apartments_{timestamp}.xlsx"

        filepath = os.path.join(self.output_dir, filename)

        try:
            # Convert to DataFrame
            df = pd.DataFrame(listings)

            # Reorder columns
            column_order = [
                'source', 'title', 'price', 'price_text', 'bedrooms',
                'bathrooms', 'sqft', 'location', 'url', 'date_posted'
            ]

            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]

            # Sort by price
            if 'price' in df.columns:
                df = df.sort_values('price', ascending=True)

            # Save to Excel with formatting
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Apartments', index=False)

                # Get the worksheet
                worksheet = writer.sheets['Apartments']

                # Auto-adjust column widths
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    # Cap at 50 characters for URL column
                    if col == 'url':
                        max_length = min(max_length, 50)
                    else:
                        max_length = min(max_length, 30)

                    worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

            logger.info(f"Generated Excel: {filepath} ({len(listings)} listings)")
            return filepath

        except Exception as e:
            logger.error(f"Error generating Excel file: {e}")
            return None

    def get_summary_stats(self, listings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for listings."""
        if not listings:
            return {
                'total_listings': 0,
                'by_source': {},
                'price_range': 'N/A',
                'avg_price': 'N/A'
            }

        df = pd.DataFrame(listings)

        stats = {
            'total_listings': len(listings),
            'by_source': df.groupby('source').size().to_dict() if 'source' in df.columns else {},
        }

        # Price statistics
        if 'price' in df.columns:
            prices = df['price'][df['price'] > 0]
            if len(prices) > 0:
                stats['price_range'] = f"${prices.min():,.0f} - ${prices.max():,.0f}"
                stats['avg_price'] = f"${prices.mean():,.0f}"
            else:
                stats['price_range'] = 'N/A'
                stats['avg_price'] = 'N/A'
        else:
            stats['price_range'] = 'N/A'
            stats['avg_price'] = 'N/A'

        return stats
