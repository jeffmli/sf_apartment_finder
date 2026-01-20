# Setup Guide

Complete step-by-step setup instructions for SF Apartment Finder.

## Prerequisites

- Python 3.8+ installed
- Git installed
- Gmail account with 2FA enabled

## Step 1: Install Python Dependencies

```bash
# Navigate to project directory
cd /home/user/sf_apartment_finder

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Set Up Gmail App Password

### Why App Password?

Google requires app-specific passwords for third-party applications accessing Gmail via SMTP.

### Steps:

1. **Enable 2-Factor Authentication**
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow the setup process

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other" (enter "Apartment Finder")
   - Click "Generate"
   - Copy the 16-character password (remove spaces)

3. **Save the Password**
   - You'll use this in your `.env` file
   - Keep it secure - never commit to git

## Step 3: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Fill in your credentials:

```env
# Email Configuration
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop  # Your 16-char app password
RECIPIENT_EMAIL=recipient@example.com
```

**Security Note**: The `.env` file is in `.gitignore` and won't be committed to git.

## Step 4: Configure Search Criteria

Edit `config.yaml` to match your apartment search needs:

```bash
nano config.yaml
```

### Example Configuration:

```yaml
search_criteria:
  # Location
  location: "San Francisco, CA"

  # Price range (monthly rent)
  min_price: 2000
  max_price: 4000

  # Bedrooms
  min_bedrooms: 1
  max_bedrooms: 2

  # Bathrooms
  min_bathrooms: 1

  # Features
  pet_friendly: false
  parking: true
  in_unit_laundry: false

  # Limits
  max_results_per_site: 50
```

### Important: Location Format

Different sites use different location formats:

- **Craigslist**: Uses subdomain (e.g., `sfbay` for SF Bay Area)
  - Update `base_url` in config if needed
- **Zillow**: Uses city-state format (e.g., "san-francisco-ca")
- **Apartments.com**: Uses city-state format (e.g., "san-francisco-ca")

## Step 5: Test the Scraper

Run a test to make sure everything works:

```bash
python main.py
```

### Expected Output:

```
2024-01-20 09:00:00 - __main__ - INFO - 🏠 SF Apartment Finder Starting...
2024-01-20 09:00:00 - __main__ - INFO - Starting apartment search...
2024-01-20 09:00:00 - __main__ - INFO - Location: San Francisco, CA
2024-01-20 09:00:01 - __main__ - INFO - --- Scraping Craigslist ---
2024-01-20 09:00:03 - __main__ - INFO - Found 25 Craigslist listings
...
2024-01-20 09:00:10 - __main__ - INFO - Sending email...
2024-01-20 09:00:12 - __main__ - INFO - ✅ Apartment search completed successfully!
```

### Check Results:

1. **Email**: Check your inbox for the apartment listings email
2. **CSV**: Check `output/` directory for the CSV file
3. **Logs**: Check `logs/` directory for detailed logs

## Step 6: Set Up Automated Daily Runs (Cron)

### For Linux/Mac:

1. **Make script executable**:
   ```bash
   chmod +x main.py
   ```

2. **Get absolute paths**:
   ```bash
   # Project directory
   pwd
   # Example output: /home/user/sf_apartment_finder

   # Python virtual environment
   which python
   # Example output: /home/user/sf_apartment_finder/venv/bin/python
   ```

3. **Edit crontab**:
   ```bash
   crontab -e
   ```

4. **Add cron job** (runs daily at 9 AM):
   ```cron
   # SF Apartment Finder - Daily at 9 AM
   0 9 * * * cd /home/user/sf_apartment_finder && /home/user/sf_apartment_finder/venv/bin/python main.py >> logs/cron.log 2>&1
   ```

5. **Save and exit** (Ctrl+X, then Y, then Enter for nano)

6. **Verify cron job**:
   ```bash
   crontab -l
   ```

### Cron Schedule Examples:

```cron
# Daily at 9 AM
0 9 * * * [command]

# Daily at 6 AM
0 6 * * * [command]

# Twice daily (9 AM and 6 PM)
0 9,18 * * * [command]

# Every Monday at 9 AM
0 9 * * 1 [command]

# Every weekday at 9 AM
0 9 * * 1-5 [command]
```

### For Windows:

Use Task Scheduler instead of cron:

1. Open Task Scheduler
2. Create Basic Task
3. Name: "SF Apartment Finder"
4. Trigger: Daily at 9:00 AM
5. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\path\to\sf_apartment_finder`

## Step 7: Verify Everything Works

### Check Logs:

```bash
# View today's log
tail -f logs/scraper_$(date +%Y%m%d).log

# View cron log
tail -f logs/cron.log
```

### Test Cron Job:

Set a cron job for 2 minutes from now to test:

```bash
# Get current time
date

# Edit crontab
crontab -e

# Add test job (adjust time)
# Example: if current time is 14:30, set for 14:32
32 14 * * * cd /home/user/sf_apartment_finder && /home/user/sf_apartment_finder/venv/bin/python main.py >> logs/cron.log 2>&1
```

Wait for the job to run, then check:

```bash
# Check if email was sent
# Check cron log
cat logs/cron.log
```

## Troubleshooting

### Issue: Email Not Sending

**Symptom**: Script runs but no email arrives

**Solutions**:
1. Verify app password is correct (16 characters, no spaces in code)
2. Check Gmail account settings
3. Look for errors in logs: `grep -i error logs/*.log`
4. Test with a simple email client to verify credentials

### Issue: No Listings Found

**Symptom**: Email says "0 listings found"

**Solutions**:
1. Relax search criteria (increase max_price, reduce min_bedrooms)
2. Check if location is correct for each site
3. Verify sites are enabled in config.yaml
4. Check logs for scraping errors

### Issue: Cron Job Not Running

**Symptom**: No emails received, no new logs

**Solutions**:
1. Check cron is running: `service cron status`
2. Check cron logs: `grep CRON /var/log/syslog`
3. Verify paths are absolute in crontab
4. Check permissions: `ls -la main.py`
5. Test script manually: `cd /path && /path/venv/bin/python main.py`

### Issue: Import Errors

**Symptom**: `ModuleNotFoundError` or `ImportError`

**Solutions**:
1. Activate virtual environment: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (needs 3.8+)

### Issue: Permission Denied

**Symptom**: Cannot write to output/ or logs/

**Solutions**:
1. Create directories: `mkdir -p output logs`
2. Fix permissions: `chmod 755 output logs`

## Advanced Configuration

### Changing Scraper Behavior

Edit individual scrapers in `src/scrapers/` to:
- Adjust timeouts
- Change user agents
- Modify parsing logic
- Add new fields

### Customizing Email Template

Edit `src/utils/email_sender.py`:
- Modify HTML/CSS in `_generate_html_email()`
- Change email structure
- Add images or styling

### Adding Filters

Edit `main.py` to add post-scraping filters:
```python
# Filter by keywords
listings = [l for l in listings if 'downtown' in l['location'].lower()]

# Filter by price per sqft
listings = [l for l in listings if l['price'] / int(l['sqft']) < 3.5]
```

## Next Steps

1. ✅ Test manual run
2. ✅ Verify email delivery
3. ✅ Set up cron job
4. ✅ Monitor for first automated run
5. ✅ Adjust search criteria as needed

## Support

If you encounter issues:
1. Check logs in `logs/` directory
2. Review configuration files
3. Test each component individually
4. Verify internet connectivity
5. Check website Terms of Service

Happy apartment hunting! 🏠
