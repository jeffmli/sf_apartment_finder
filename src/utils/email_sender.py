"""Email sending utilities."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class EmailSender:
    """Send emails with apartment listings."""

    def __init__(self, sender_email: str, sender_password: str):
        """Initialize email sender."""
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_apartment_email(
        self,
        recipient_email: str,
        listings: List[Dict[str, Any]],
        attachment_path: Optional[str] = None,
        subject: Optional[str] = None,
        stats: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send email with apartment listings."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')

            if not subject:
                date_str = datetime.now().strftime("%B %d, %Y")
                subject = f"Daily Apartment Listings - {date_str}"

            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            # Generate HTML content
            html_content = self._generate_html_email(listings, stats)

            # Attach HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Attach CSV file if provided
            if attachment_path and os.path.exists(attachment_path):
                try:
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())

                    encoders.encode_base64(part)
                    filename = os.path.basename(attachment_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    msg.attach(part)
                    logger.info(f"Attached file: {filename}")
                except Exception as e:
                    logger.error(f"Error attaching file: {e}")

            # Send email
            logger.info(f"Sending email to {recipient_email}...")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info("Email sent successfully!")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def _generate_html_email(
        self,
        listings: List[Dict[str, Any]],
        stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate HTML email content."""
        date_str = datetime.now().strftime("%B %d, %Y")

        # Start HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                .summary {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .summary h2 {{
                    margin-top: 0;
                    color: #2c3e50;
                }}
                .stat {{
                    display: inline-block;
                    margin-right: 20px;
                    padding: 10px;
                }}
                .stat-label {{
                    font-weight: bold;
                    color: #7f8c8d;
                }}
                .stat-value {{
                    font-size: 1.2em;
                    color: #2980b9;
                }}
                .listing {{
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 15px 0;
                    background-color: #fff;
                    transition: box-shadow 0.3s;
                }}
                .listing:hover {{
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .listing-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: start;
                    margin-bottom: 10px;
                }}
                .listing-title {{
                    font-size: 1.1em;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 0;
                }}
                .listing-price {{
                    font-size: 1.3em;
                    font-weight: bold;
                    color: #27ae60;
                }}
                .listing-details {{
                    color: #7f8c8d;
                    margin: 5px 0;
                }}
                .listing-source {{
                    display: inline-block;
                    padding: 3px 8px;
                    background-color: #3498db;
                    color: white;
                    border-radius: 3px;
                    font-size: 0.85em;
                    margin-bottom: 8px;
                }}
                .listing-link {{
                    display: inline-block;
                    margin-top: 10px;
                    padding: 8px 15px;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }}
                .listing-link:hover {{
                    background-color: #2980b9;
                }}
                .no-listings {{
                    text-align: center;
                    padding: 40px;
                    color: #7f8c8d;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <h1>🏠 Daily Apartment Listings</h1>
            <p><strong>Date:</strong> {date_str}</p>
        """

        # Add summary statistics
        if stats:
            html += """
            <div class="summary">
                <h2>Summary</h2>
            """

            total = stats.get('total_listings', 0)
            html += f'<div class="stat"><span class="stat-label">Total Listings:</span> <span class="stat-value">{total}</span></div>'

            if 'price_range' in stats and stats['price_range'] != 'N/A':
                html += f'<div class="stat"><span class="stat-label">Price Range:</span> <span class="stat-value">{stats["price_range"]}</span></div>'

            if 'avg_price' in stats and stats['avg_price'] != 'N/A':
                html += f'<div class="stat"><span class="stat-label">Average Price:</span> <span class="stat-value">{stats["avg_price"]}</span></div>'

            if 'by_source' in stats:
                html += '<br><div style="margin-top: 10px;">'
                for source, count in stats['by_source'].items():
                    html += f'<div class="stat"><span class="stat-label">{source}:</span> <span class="stat-value">{count}</span></div>'
                html += '</div>'

            html += "</div>"

        # Add listings
        if listings:
            # Limit to max_listings for email display
            max_display = 30
            display_listings = listings[:max_display]

            for listing in display_listings:
                source = listing.get('source', 'Unknown')
                title = listing.get('title', 'No Title')
                price_text = listing.get('price_text', 'N/A')
                bedrooms = listing.get('bedrooms', 'N/A')
                bathrooms = listing.get('bathrooms', 'N/A')
                sqft = listing.get('sqft', 'N/A')
                location = listing.get('location', 'N/A')
                url = listing.get('url', '#')

                html += f"""
                <div class="listing">
                    <span class="listing-source">{source}</span>
                    <div class="listing-header">
                        <h3 class="listing-title">{title}</h3>
                        <div class="listing-price">{price_text}</div>
                    </div>
                    <div class="listing-details">
                        📍 {location}
                    </div>
                    <div class="listing-details">
                        🛏️ {bedrooms} bed | 🚿 {bathrooms} bath | 📐 {sqft} sqft
                    </div>
                    <a href="{url}" class="listing-link" target="_blank">View Listing</a>
                </div>
                """

            if len(listings) > max_display:
                html += f"""
                <div class="summary" style="text-align: center;">
                    <p>Showing {max_display} of {len(listings)} listings. See attached CSV for complete list.</p>
                </div>
                """
        else:
            html += """
            <div class="no-listings">
                <p>No apartment listings found matching your criteria.</p>
            </div>
            """

        # Footer
        html += """
            <div class="footer">
                <p>This is an automated apartment listing email.</p>
                <p>See attached CSV file for the complete spreadsheet of listings.</p>
            </div>
        </body>
        </html>
        """

        return html
