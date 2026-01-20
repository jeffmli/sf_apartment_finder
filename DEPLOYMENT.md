# Deployment Guide - Running Daily Apartment Scraper

Complete guide to deploying your apartment scraper to run automatically every day.

## Option 1: Local Machine with Cron ⭐ (Recommended for Testing)

**Best for**: Running on your personal computer (Mac/Linux)

### Requirements
- Computer must be on and connected to internet at scheduled time
- Linux, Mac, or WSL on Windows

### Setup Steps

1. **Complete initial setup**:
   ```bash
   cd /home/user/sf_apartment_finder
   ./setup.sh
   # Edit .env with your email credentials
   # Edit config.yaml with your search criteria
   ```

2. **Test manually first**:
   ```bash
   source venv/bin/activate
   python main.py
   ```
   Check your email to verify it works!

3. **Get absolute paths**:
   ```bash
   # Project directory
   pwd
   # Output: /home/user/sf_apartment_finder

   # Python path
   realpath venv/bin/python
   # Output: /home/user/sf_apartment_finder/venv/bin/python
   ```

4. **Create cron job**:
   ```bash
   crontab -e
   ```

5. **Add this line** (runs daily at 9 AM):
   ```cron
   0 9 * * * cd /home/user/sf_apartment_finder && /home/user/sf_apartment_finder/venv/bin/python main.py >> logs/cron.log 2>&1
   ```

6. **Verify**:
   ```bash
   crontab -l
   ```

### Pros & Cons

✅ **Pros:**
- Free
- Simple setup
- Full control
- No external dependencies

❌ **Cons:**
- Computer must stay on
- Won't run if computer is off/asleep
- Not suitable for laptops that travel

---

## Option 2: Raspberry Pi / Always-On Server ⭐⭐ (Best for Home Use)

**Best for**: Reliable home deployment without cloud costs

### Requirements
- Raspberry Pi (any model) or old computer
- Constant internet connection
- Power supply

### Setup Steps

Same as Option 1, but on your Raspberry Pi:

1. **SSH into your Pi**:
   ```bash
   ssh pi@raspberrypi.local
   ```

2. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd sf_apartment_finder
   ./setup.sh
   ```

3. **Configure**:
   - Edit `.env` with email credentials
   - Edit `config.yaml` with search criteria

4. **Set up cron**:
   ```bash
   crontab -e
   # Add: 0 9 * * * cd /home/pi/sf_apartment_finder && /home/pi/sf_apartment_finder/venv/bin/python main.py >> logs/cron.log 2>&1
   ```

### Pros & Cons

✅ **Pros:**
- Reliable 24/7 operation
- One-time hardware cost
- No monthly fees
- Full control

❌ **Cons:**
- Initial hardware cost ($35+)
- Requires basic setup knowledge
- Home network dependency

---

## Option 3: AWS EC2 (Free Tier) ⭐⭐⭐ (Best for Cloud)

**Best for**: Reliable cloud deployment with minimal cost

### Cost: FREE for first 12 months, then ~$5-10/month

### Setup Steps

1. **Create AWS account**: https://aws.amazon.com

2. **Launch EC2 instance**:
   - Go to EC2 Dashboard
   - Click "Launch Instance"
   - Choose "Ubuntu Server 22.04 LTS"
   - Instance type: `t2.micro` (free tier)
   - Create/download SSH key pair
   - Configure security group (no inbound needed)
   - Launch instance

3. **Connect to instance**:
   ```bash
   ssh -i your-key.pem ubuntu@<instance-public-ip>
   ```

4. **Setup on EC2**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python and dependencies
   sudo apt install python3-pip python3-venv git -y

   # Clone repository
   git clone <your-repo-url>
   cd sf_apartment_finder

   # Run setup
   chmod +x setup.sh
   ./setup.sh

   # Configure
   nano .env        # Add your email credentials
   nano config.yaml # Set your search criteria

   # Test
   source venv/bin/activate
   python main.py
   ```

5. **Set up cron**:
   ```bash
   crontab -e
   # Add: 0 9 * * * cd /home/ubuntu/sf_apartment_finder && /home/ubuntu/sf_apartment_finder/venv/bin/python main.py >> logs/cron.log 2>&1
   ```

6. **Keep instance running**:
   - Your instance will stay on 24/7
   - Check AWS billing dashboard

### Pros & Cons

✅ **Pros:**
- Reliable 24/7 operation
- Free for 12 months
- Accessible from anywhere
- Professional solution

❌ **Cons:**
- Costs after free tier (~$5-10/mo)
- Requires AWS account
- Slightly more complex setup

---

## Option 4: GitHub Actions ⭐⭐⭐ (Best Free Cloud Option)

**Best for**: Completely free cloud deployment

### Cost: FREE (2,000 minutes/month)

### Setup Steps

1. **Push code to GitHub** (if not already):
   ```bash
   git remote add origin https://github.com/yourusername/sf_apartment_finder.git
   git push -u origin main
   ```

2. **Add GitHub Secrets**:
   - Go to your repo on GitHub
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add these secrets:
     - `SENDER_EMAIL`: your Gmail address
     - `SENDER_PASSWORD`: your Gmail app password
     - `RECIPIENT_EMAIL`: where to send listings

3. **Create workflow file**:
   ```bash
   mkdir -p .github/workflows
   ```

4. **Create `.github/workflows/daily-scraper.yml`**:
   ```yaml
   name: Daily Apartment Scraper

   on:
     schedule:
       - cron: '0 9 * * *'  # 9 AM UTC daily
     workflow_dispatch:  # Allow manual trigger

   jobs:
     scrape:
       runs-on: ubuntu-latest

       steps:
       - name: Checkout code
         uses: actions/checkout@v3

       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.10'

       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -r requirements.txt

       - name: Create .env file
         run: |
           echo "SENDER_EMAIL=${{ secrets.SENDER_EMAIL }}" > .env
           echo "SENDER_PASSWORD=${{ secrets.SENDER_PASSWORD }}" >> .env
           echo "RECIPIENT_EMAIL=${{ secrets.RECIPIENT_EMAIL }}" >> .env

       - name: Run scraper
         run: python main.py

       - name: Upload logs
         if: always()
         uses: actions/upload-artifact@v3
         with:
           name: scraper-logs
           path: logs/
   ```

5. **Push to GitHub**:
   ```bash
   git add .github/workflows/daily-scraper.yml
   git commit -m "Add GitHub Actions workflow"
   git push
   ```

6. **Verify**:
   - Go to Actions tab in your GitHub repo
   - Click "Run workflow" to test manually
   - Check your email!

### Pros & Cons

✅ **Pros:**
- Completely FREE
- No server management
- Version controlled
- Easy to modify schedule
- Runs in the cloud

❌ **Cons:**
- Public repo or GitHub Pro required
- 2,000 minute/month limit (plenty for this use)
- Logs stored in GitHub (privacy concern)
- Slight delay variance in execution time

---

## Option 5: Google Cloud Platform (Free Tier)

**Similar to AWS but different provider**

### Cost: FREE for first 90 days, then ~$5-10/month

### Setup Steps

1. **Create GCP account**: https://cloud.google.com
2. **Create Compute Engine instance** (similar to AWS EC2)
3. **Follow same setup as AWS EC2 option**

---

## Option 6: Heroku (Simplified Cloud)

**Best for**: Easiest cloud deployment

### Cost: $7/month (Eco Dyno)

### Setup Steps

1. **Install Heroku CLI**:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create app**:
   ```bash
   heroku create apartment-finder-yourname
   ```

4. **Add scheduler addon**:
   ```bash
   heroku addons:create scheduler:standard
   ```

5. **Set environment variables**:
   ```bash
   heroku config:set SENDER_EMAIL=your-email@gmail.com
   heroku config:set SENDER_PASSWORD=your-app-password
   heroku config:set RECIPIENT_EMAIL=recipient@example.com
   ```

6. **Create `Procfile`**:
   ```
   worker: python main.py
   ```

7. **Deploy**:
   ```bash
   git add Procfile
   git commit -m "Add Procfile"
   git push heroku main
   ```

8. **Configure scheduler**:
   ```bash
   heroku addons:open scheduler
   # Add job: python main.py
   # Schedule: Daily at 9:00 AM
   ```

---

## Comparison Table

| Option | Cost | Reliability | Setup Difficulty | Best For |
|--------|------|-------------|------------------|----------|
| **Local Cron** | Free | Low (computer must be on) | Easy | Testing |
| **Raspberry Pi** | $35 one-time | High | Medium | Home users |
| **AWS EC2** | Free 12mo, then $5-10/mo | Very High | Medium | Professional |
| **GitHub Actions** | Free | High | Easy | Free cloud option |
| **GCP** | Similar to AWS | Very High | Medium | AWS alternative |
| **Heroku** | $7/mo | High | Easy | Easiest cloud |

---

## My Recommendation

**For most users**: Start with **GitHub Actions** ⭐⭐⭐

**Why?**
- ✅ Completely free
- ✅ No server management
- ✅ Easy to set up
- ✅ Reliable
- ✅ Can modify schedule easily
- ✅ Version controlled

**Alternative**: If you want privacy and have a spare computer or Raspberry Pi, use **local cron** or **Pi deployment**.

---

## Step-by-Step: GitHub Actions (Recommended)

Let me walk you through the GitHub Actions setup:

### 1. Make Sure Code is in GitHub

```bash
cd /home/user/sf_apartment_finder

# If not already connected to GitHub
git remote add origin https://github.com/YOUR_USERNAME/sf_apartment_finder.git
git push -u origin claude/apartment-scraper-email-VY8fs
```

### 2. Add Secrets to GitHub

1. Go to: `https://github.com/YOUR_USERNAME/sf_apartment_finder`
2. Click **Settings** (top right)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**
5. Add three secrets:
   - Name: `SENDER_EMAIL`, Value: `your-email@gmail.com`
   - Name: `SENDER_PASSWORD`, Value: `your-gmail-app-password`
   - Name: `RECIPIENT_EMAIL`, Value: `where-to-send@example.com`

### 3. Create Workflow File

Create this file in your repo:

**`.github/workflows/daily-scraper.yml`**

I'll create this for you:
