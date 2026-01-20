# SF Apartment Finder

An automated apartment scraper that searches Craigslist, Zillow, and Apartments.com for rental listings and sends daily email newsletters with results.

## Features

- **Multi-source scraping**: Searches Craigslist, Zillow, and Apartments.com
- **Customizable criteria**: Filter by price, bedrooms, bathrooms, location, and more
- **Automated emails**: Daily HTML newsletters with apartment listings
- **CSV exports**: Downloadable spreadsheet with all results
- **Easy scheduling**: Set up with cron for automated daily searches

## Requirements

- Python 3.8 or higher
- Gmail account (for sending emails)
- Internet connection

## Quick Start

### 1. Clone and Setup

```bash
cd /home/user/sf_apartment_finder
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Email

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-specific-password
RECIPIENT_EMAIL=recipient@example.com
```

**Important**: For Gmail, you need to create an **App-Specific Password**:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a new app password for "Mail"
5. Use this password in your `.env` file

### 3. Configure Search Criteria

Edit `config.yaml` to set your apartment search preferences:

```yaml
search_criteria:
  location: "San Francisco, CA"
  min_price: 1500
  max_price: 3500
  min_bedrooms: 1
  max_bedrooms: 2
  min_bathrooms: 1
  pet_friendly: false
  parking: false
  in_unit_laundry: false
```

### 4. Run the Scraper

```bash
python main.py
```

The scraper will:
1. Search all enabled sites
2. Generate a CSV file in the `output/` directory
3. Send an HTML email with listings and CSV attachment

## Scheduling with Cron

To run automatically every day at 9 AM:

### Linux/Mac

1. Open crontab editor:
   ```bash
   crontab -e
   ```

2. Add this line (adjust path as needed):
   ```cron
   0 9 * * * cd /home/user/sf_apartment_finder && /home/user/sf_apartment_finder/venv/bin/python main.py >> logs/cron.log 2>&1
   ```

3. Save and exit

### Verify Cron Job

```bash
crontab -l
```

## Project Structure

```
sf_apartment_finder/
├── main.py                          # Main orchestrator script
├── config.yaml                      # Search criteria configuration
├── .env                             # Email credentials (create from .env.example)
├── requirements.txt                 # Python dependencies
├── src/
│   ├── config_loader.py            # Configuration management
│   ├── scrapers/
│   │   ├── craigslist_scraper.py   # Craigslist scraper
│   │   ├── zillow_scraper.py       # Zillow scraper
│   │   └── apartments_scraper.py   # Apartments.com scraper
│   └── utils/
│       ├── email_sender.py         # Email functionality
│       └── spreadsheet_generator.py # CSV generation
├── output/                          # Generated CSV files
└── logs/                            # Log files
```

## Configuration Options

### Search Criteria (`config.yaml`)

| Option | Description | Example |
|--------|-------------|---------|
| `location` | City and state | `"San Francisco, CA"` |
| `min_price` | Minimum monthly rent | `1500` |
| `max_price` | Maximum monthly rent | `3500` |
| `min_bedrooms` | Minimum bedrooms | `1` |
| `max_bedrooms` | Maximum bedrooms | `2` |
| `min_bathrooms` | Minimum bathrooms | `1` |
| `pet_friendly` | Pets allowed | `true/false` |
| `parking` | Parking included | `true/false` |
| `in_unit_laundry` | In-unit laundry | `true/false` |
| `max_results_per_site` | Max results per site | `50` |

### Scraper Settings

Enable/disable specific scrapers:

```yaml
scrapers:
  craigslist:
    enabled: true
  zillow:
    enabled: true
  apartments_com:
    enabled: true
```

### Email Settings

```yaml
email:
  subject: "Daily Apartment Listings - {date}"
  max_listings_in_email: 30
```

## Troubleshooting

### Email Not Sending

- **Check credentials**: Verify SENDER_EMAIL and SENDER_PASSWORD in `.env`
- **App password**: Make sure you're using an app-specific password, not your regular Gmail password
- **2FA enabled**: Gmail requires 2-factor authentication for app passwords
- **Less secure apps**: Ensure "Less secure app access" is NOT turned on (use app passwords instead)

### No Listings Found

- **Check criteria**: Your filters might be too restrictive
- **Location**: Verify the location string matches the site's format
- **Site blocking**: Some sites may block automated requests
  - Try reducing `max_results_per_site`
  - Add delays between runs
  - Check logs for specific errors

### Scraper Errors & 403 Forbidden

**Important**: Zillow and Apartments.com have sophisticated anti-bot protection that often blocks scrapers with 403 Forbidden errors.

**If you see 403 errors:**

1. **Disable problematic scrapers** - Edit `config.yaml`:
   ```yaml
   scrapers:
     craigslist:
       enabled: true    # Keep this one - usually works
     zillow:
       enabled: false   # Disable if getting 403 errors
     apartments_com:
       enabled: false   # Disable if getting 403 errors
   ```

2. **Rely on Craigslist** - It's the most reliable and scraper-friendly
3. **Check logs**: Review `logs/scraper_YYYYMMDD.log` for detailed error messages

**Why this happens:**
- Zillow and Apartments.com detect automated requests
- They use CAPTCHAs and sophisticated fingerprinting
- Even with rotating user agents and delays, they may block requests
- This is normal behavior for these sites

**Alternatives:**
- Use only Craigslist (usually sufficient for most searches)
- Manually browse Zillow/Apartments.com instead
- Consider using official APIs if available (often paid)

### Cron Job Not Running

- **Check cron logs**: `grep CRON /var/log/syslog`
- **Verify path**: Make sure all paths in crontab are absolute
- **Python path**: Ensure you're using the correct Python from venv
- **Permissions**: Verify the script has execute permissions: `chmod +x main.py`

## Limitations & Legal Considerations

- **Scraping legality**: Web scraping may violate Terms of Service
  - Craigslist: Generally more permissive
  - Zillow: Has anti-scraping measures
  - Apartments.com: May block automated requests
- **Rate limiting**: Be respectful of websites
- **Personal use**: This tool is intended for personal apartment hunting
- **No guarantees**: Listings may be outdated or removed

## Customization

### Adding New Scrapers

1. Create a new scraper in `src/scrapers/`
2. Extend `BaseScraper` class
3. Implement `scrape()` method
4. Add configuration to `config.yaml`
5. Import and use in `main.py`

### Changing Email Template

Edit the `_generate_html_email()` method in `src/utils/email_sender.py` to customize the HTML template.

### Adding Features

Common additions:
- Image scraping and display
- Distance/commute calculations
- Machine learning to rank listings
- Text message notifications
- Database storage for tracking

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review configuration in `config.yaml` and `.env`
3. Verify dependencies are installed: `pip install -r requirements.txt`

## License

This project is for personal use only. Please respect the Terms of Service of all websites being scraped.
