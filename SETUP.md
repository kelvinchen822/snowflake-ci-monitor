# Setup Guide - Competitive Intelligence Monitor

This guide will walk you through setting up the CI monitor from scratch.

## Table of Contents

1. [SendGrid Setup](#sendgrid-setup)
2. [GitHub Repository Setup](#github-repository-setup)
3. [Local Testing](#local-testing)
4. [Deployment](#deployment)
5. [Troubleshooting](#troubleshooting)

---

## SendGrid Setup

### Step 1: Create SendGrid Account

1. Go to [sendgrid.com](https://sendgrid.com)
2. Click **Sign Up** (choose Free plan - 100 emails/day)
3. Complete registration with your email
4. Verify your email address

### Step 2: Verify Sender Identity

**Important**: SendGrid requires sender verification to prevent spam.

1. Log in to SendGrid dashboard
2. Navigate to **Settings** → **Sender Authentication**
3. Click **Verify a Single Sender**
4. Fill out the form:
   - **From Name**: Snowflake CI Monitor
   - **From Email Address**: chen.kelvin822@gmail.com (or your corporate email)
   - **Reply To**: (same as From Email)
   - **Company Address**: (fill in)
5. Click **Create**
6. Check your email for verification link
7. Click the verification link

**Note**: Until you verify your sender, emails won't be delivered.

### Step 3: Create API Key

1. In SendGrid dashboard, go to **Settings** → **API Keys**
2. Click **Create API Key**
3. Settings:
   - **API Key Name**: `Snowflake-CI-Monitor`
   - **API Key Permissions**: Select **Restricted Access**
   - Under **Mail Send**, toggle **Mail Send** to **FULL ACCESS**
   - Leave all other permissions as **No Access**
4. Click **Create & View**
5. **IMPORTANT**: Copy the API key immediately (you won't see it again)
6. Save it securely (you'll need it for GitHub Secrets)

Example API key format: `SG.xxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy`

---

## GitHub Repository Setup

### Step 1: Create Repository

1. Go to [github.com](https://github.com)
2. Click **New repository** (or go to github.com/new)
3. Settings:
   - **Repository name**: `snowflake-ci-monitor`
   - **Description**: Competitive Intelligence Monitor for Snowflake BD
   - **Visibility**: **Private** (recommended)
   - **Initialize**: Do NOT check any boxes (we'll push existing code)
4. Click **Create repository**

### Step 2: Configure GitHub Secrets

1. In your new repository, click **Settings** (top right)
2. In left sidebar, click **Secrets and variables** → **Actions**
3. Click **New repository secret**

**Secret 1: SENDGRID_API_KEY**
- Name: `SENDGRID_API_KEY`
- Value: Paste your SendGrid API key from earlier
- Click **Add secret**

**Secret 2: RECIPIENT_EMAIL**
- Click **New repository secret** again
- Name: `RECIPIENT_EMAIL`
- Value: `chen.kelvin822@gmail.com`
- Click **Add secret**

### Step 3: Enable GitHub Actions

1. Go to **Settings** → **Actions** → **General**
2. Under **Actions permissions**, select:
   - ✅ **Allow all actions and reusable workflows**
3. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
4. Click **Save**

---

## Local Testing

Before deploying, test the setup locally to ensure everything works.

### Step 1: Clone Repository

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/snowflake-ci-monitor.git
cd snowflake-ci-monitor

# Copy the code files into this directory
# (if you haven't already pushed them)
```

### Step 2: Set Up Python Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

**Windows (PowerShell):**
```powershell
@"
SENDGRID_API_KEY=your_sendgrid_api_key_here
RECIPIENT_EMAIL=chen.kelvin822@gmail.com
"@ | Out-File -FilePath .env -Encoding utf8
```

**Mac/Linux:**
```bash
cat > .env << EOF
SENDGRID_API_KEY=your_sendgrid_api_key_here
RECIPIENT_EMAIL=chen.kelvin822@gmail.com
EOF
```

**Or manually create `.env` file:**
```
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
RECIPIENT_EMAIL=chen.kelvin822@gmail.com
```

### Step 4: Initialize Database

```bash
python main.py --init
```

**Expected output:**
```
Initializing database...
Database tables created successfully
Competitor data seeded successfully
✓ Database initialized successfully
```

### Step 5: Send Test Email

```bash
python main.py --test
```

**Expected output:**
```
============================================================
SNOWFLAKE COMPETITIVE INTELLIGENCE MONITOR
============================================================
Started at: 2024-01-16 10:30:00

============================================================
GENERATING REPORT
============================================================

Sending email...
✓ Email sent successfully to chen.kelvin822@gmail.com
  Status code: 202
✓ Report sent successfully

============================================================
✓ Pipeline completed in 2.34 seconds
============================================================
```

**Check your email** (including spam folder) for the test email.

### Step 6: Run Full Pipeline (Optional)

```bash
python main.py
```

This will:
1. Collect signals from RSS feeds
2. Classify and deduplicate them
3. Store in database
4. Send email report

---

## Deployment

### Step 1: Push Code to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Initial CI monitor setup"

# Push to GitHub
git push origin main
```

### Step 2: Verify Workflow File

1. Go to your GitHub repository
2. Click **Actions** tab
3. You should see **Daily Competitive Intelligence Monitor** workflow

### Step 3: Manual Test Run

1. In Actions tab, click on the workflow name
2. Click **Run workflow** (right side)
3. Keep branch as `main`
4. Click **Run workflow**

### Step 4: Monitor Execution

1. A new workflow run will appear
2. Click on it to see progress
3. Click **monitor** job to see detailed logs
4. Watch for:
   - ✅ Checkout repository
   - ✅ Set up Python
   - ✅ Install dependencies
   - ✅ Run monitoring pipeline
   - ✅ Commit database updates

### Step 5: Verify Email Delivery

Check your inbox (chen.kelvin822@gmail.com) for the report.

---

## Troubleshooting

### Email Not Received

**Problem**: Test email sent but not received

**Solutions**:
1. **Check spam folder** - First-time emails often go to spam
2. **Verify sender in SendGrid**:
   - Go to SendGrid → Settings → Sender Authentication
   - Ensure chen.kelvin822@gmail.com is verified (green checkmark)
3. **Check SendGrid Activity Feed**:
   - SendGrid Dashboard → Activity Feed
   - Look for your email - status should be "Delivered"
   - If "Blocked" or "Bounced", check sender verification

**Problem**: SendGrid says "Forbidden"

**Solution**: API key doesn't have Mail Send permission:
1. Go to SendGrid → Settings → API Keys
2. Delete old key
3. Create new key with **Full Access** to **Mail Send**

### GitHub Actions Failed

**Problem**: Workflow run shows red X

**Solutions**:
1. **Click on the failed run** to see logs
2. Common errors:

**Error: `SENDGRID_API_KEY not set`**
- Go to Settings → Secrets → Actions
- Verify `SENDGRID_API_KEY` secret exists
- Re-add if necessary

**Error: `Permission denied` during commit**
- Go to Settings → Actions → General
- Under Workflow permissions, select **Read and write permissions**
- Click Save

**Error: `ModuleNotFoundError`**
- Check `requirements.txt` exists
- Verify all dependencies are listed

### RSS Feed Issues

**Problem**: No signals collected

**Solutions**:
1. **Check if feeds are accessible**:
   ```bash
   python -c "import feedparser; print(feedparser.parse('https://www.databricks.com/blog/feed').entries[0].title)"
   ```
2. **Increase lookback period**:
   - Edit `.env`: `LOOKBACK_DAYS=7`
3. **Check feed URLs in `config/competitors.json`**
   - Competitors may have changed their RSS URLs

### Database Issues

**Problem**: Database locked or corrupt

**Solution**:
```bash
# Delete database and reinitialize
rm data/intelligence.db
python main.py --init
```

### Local Environment Issues

**Problem**: `ModuleNotFoundError` when running locally

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem**: Python version too old

**Solution**:
```bash
# Check Python version
python --version  # Should be 3.10 or higher

# If too old, install Python 3.10+
# Then create new venv with correct version
python3.10 -m venv venv
```

---

## Verification Checklist

Use this checklist to ensure everything is set up correctly:

- [ ] SendGrid account created (free tier)
- [ ] Sender email verified in SendGrid
- [ ] SendGrid API key created with Mail Send permissions
- [ ] GitHub repository created (private)
- [ ] GitHub Secrets added (SENDGRID_API_KEY, RECIPIENT_EMAIL)
- [ ] GitHub Actions enabled with write permissions
- [ ] Local test successful (`python main.py --test`)
- [ ] Test email received in inbox
- [ ] Code pushed to GitHub
- [ ] Manual workflow run successful
- [ ] Report email received from GitHub Actions run
- [ ] Workflow scheduled for 8 AM ET daily

---

## Next Steps

After successful setup:

1. **Wait for first scheduled run** (8 AM ET next day)
2. **Review email report** for signal quality
3. **Adjust keywords** in `src/config.py` if needed
4. **Monitor weekly** via GitHub Actions tab

## Support Resources

- **SendGrid Documentation**: https://docs.sendgrid.com/
- **GitHub Actions Documentation**: https://docs.github.com/en/actions
- **Project README**: [README.md](README.md)

---

## Quick Reference

### Useful Commands

```bash
# Initialize database
python main.py --init

# Send test email
python main.py --test

# Run full pipeline
python main.py

# Check Python version
python --version

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

### Important URLs

- SendGrid Dashboard: https://app.sendgrid.com/
- GitHub Actions: https://github.com/YOUR_USERNAME/snowflake-ci-monitor/actions
- Repository Settings: https://github.com/YOUR_USERNAME/snowflake-ci-monitor/settings

### Key Files

- `main.py` - Entry point
- `src/config.py` - Configuration
- `config/competitors.json` - Competitor definitions
- `.github/workflows/daily-monitor.yml` - GitHub Actions workflow
- `requirements.txt` - Python dependencies
- `.env` - Local environment variables (DO NOT COMMIT)
