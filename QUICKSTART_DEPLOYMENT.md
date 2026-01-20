# Quick Start: Deploy in 10 Minutes with GitHub Actions

The fastest way to get your apartment scraper running daily in the cloud - **completely free**.

## Prerequisites

- GitHub account (free)
- Gmail account with app-specific password
- This code pushed to GitHub

## Steps

### 1. Push Code to GitHub (2 minutes)

If you haven't already:

```bash
cd /home/user/sf_apartment_finder

# Create a new repo on GitHub first at: https://github.com/new
# Then connect and push:

git remote add origin https://github.com/YOUR_USERNAME/sf_apartment_finder.git
git push -u origin claude/apartment-scraper-email-VY8fs
```

### 2. Configure Secrets (3 minutes)

1. **Go to your GitHub repo**: `https://github.com/YOUR_USERNAME/sf_apartment_finder`

2. **Click Settings** (top navigation)

3. **Click "Secrets and variables"** → **"Actions"** (left sidebar)

4. **Click "New repository secret"** and add each of these:

   **Secret 1:**
   - Name: `SENDER_EMAIL`
   - Value: Your Gmail address (e.g., `yourname@gmail.com`)

   **Secret 2:**
   - Name: `SENDER_PASSWORD`
   - Value: Your Gmail app-specific password
     - Get this at: https://myaccount.google.com/apppasswords
     - Generate password for "Mail"
     - Copy the 16-character code

   **Secret 3:**
   - Name: `RECIPIENT_EMAIL`
   - Value: Where to send apartment listings (can be same as sender)

### 3. Configure Search Criteria (2 minutes)

Edit `config.yaml` on GitHub or locally:

```yaml
search_criteria:
  location: "San Francisco, CA"  # Change to your city
  min_price: 1500
  max_price: 3500
  min_bedrooms: 1
  max_bedrooms: 2
```

If editing locally:
```bash
nano config.yaml
git add config.yaml
git commit -m "Update search criteria"
git push
```

### 4. Test the Workflow (1 minute)

1. **Go to Actions tab** in your GitHub repo

2. **Click "Daily Apartment Scraper"** workflow (left sidebar)

3. **Click "Run workflow"** → **"Run workflow"** button

4. **Wait ~1-2 minutes** for it to complete

5. **Check your email!** You should receive apartment listings

### 5. Verify Daily Schedule (1 minute)

The workflow is already configured to run daily at 9 AM UTC.

**Check your timezone:**
- **US Pacific**: 9 AM UTC = 1 AM PST / 2 AM PDT
- **US Eastern**: 9 AM UTC = 4 AM EST / 5 AM EDT
- **US Central**: 9 AM UTC = 3 AM CST / 4 AM CDT

**To change the schedule**, edit `.github/workflows/daily-scraper.yml`:

```yaml
schedule:
  - cron: '0 14 * * *'  # 2 PM UTC = 9 AM EST
```

Cron time converter: https://crontab.guru/

Common schedules:
```yaml
- cron: '0 13 * * *'  # 1 PM UTC = 9 AM EDT / 6 AM PDT
- cron: '0 14 * * *'  # 2 PM UTC = 10 AM EDT / 7 AM PDT
- cron: '0 15 * * *'  # 3 PM UTC = 11 AM EDT / 8 AM PDT
```

Commit and push any changes:
```bash
git add .github/workflows/daily-scraper.yml
git commit -m "Update schedule"
git push
```

---

## That's It! 🎉

Your apartment scraper is now deployed and will run automatically every day.

### What Happens Now?

1. **Daily execution**: GitHub Actions runs the scraper at your scheduled time
2. **Email delivery**: You receive an HTML email with listings + CSV attachment
3. **Automatic**: No maintenance required
4. **Free**: Completely free with GitHub's 2,000 minutes/month

### Troubleshooting

**No email received?**
1. Check GitHub Actions tab → Latest run → View logs
2. Verify secrets are set correctly (Settings → Secrets)
3. Check spam folder
4. Verify Gmail app password is correct

**Want to run more frequently?**

Edit the cron schedule:
```yaml
# Twice daily (9 AM and 5 PM UTC)
schedule:
  - cron: '0 9,17 * * *'

# Every 12 hours
schedule:
  - cron: '0 */12 * * *'
```

**View execution history:**
- Go to Actions tab
- See all past runs
- Download logs and CSV files (stored for 7/30 days)

### Monitoring

**Check if it's working:**
1. Go to Actions tab
2. See green checkmark ✅ = success
3. Red X ❌ = failed (click to see error logs)
4. Download artifacts to see logs and CSV files

**Email not working but workflow succeeds?**
- Check the logs in Actions → Latest run → scrape-apartments → Run apartment scraper
- Look for email sending errors
- Verify SMTP settings and credentials

---

## Alternative: Local Cron (If You Prefer)

Don't want to use GitHub Actions? Run locally:

```bash
crontab -e
```

Add this line (runs daily at 9 AM):
```cron
0 9 * * * cd /home/user/sf_apartment_finder && /home/user/sf_apartment_finder/venv/bin/python main.py >> logs/cron.log 2>&1
```

**Note**: Your computer must be on at 9 AM daily.

---

## Next Steps

- ✅ Monitor your first few daily runs
- ✅ Adjust search criteria in `config.yaml` as needed
- ✅ Check spam folder if emails don't arrive
- ✅ Refine bedrooms/price ranges based on results

Happy apartment hunting! 🏠
