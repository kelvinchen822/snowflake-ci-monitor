# Quick Start - 5 Minutes to Deploy

Get your Competitive Intelligence Monitor running in just 5 minutes.

## Prerequisites

- GitHub account
- Email account (for SendGrid)

## Step 1: SendGrid (2 minutes)

1. Go to [sendgrid.com](https://sendgrid.com) → Sign up (free)
2. Verify your email
3. **Settings** → **Sender Authentication** → **Verify a Single Sender**
   - Use: chen.kelvin822@gmail.com
   - Click verification link in email
4. **Settings** → **API Keys** → **Create API Key**
   - Name: `Snowflake-CI`
   - Permission: **Mail Send** = Full Access
   - Copy the API key (starts with `SG.`)

## Step 2: GitHub Repository (2 minutes)

1. Go to [github.com/new](https://github.com/new)
2. Create private repository: `snowflake-ci-monitor`
3. Go to **Settings** → **Secrets and variables** → **Actions**
4. Add two secrets:
   - `SENDGRID_API_KEY` = your API key from Step 1
   - `RECIPIENT_EMAIL` = chen.kelvin822@gmail.com
5. Go to **Settings** → **Actions** → **General**
   - Enable "Read and write permissions"

## Step 3: Deploy (1 minute)

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/snowflake-ci-monitor.git
cd snowflake-ci-monitor

# Copy all files from competitive-intelligence/ folder into this directory

# Push to GitHub
git add .
git commit -m "Initial setup"
git push origin main
```

## Step 4: Test

1. Go to **Actions** tab on GitHub
2. Click **Daily Competitive Intelligence Monitor**
3. Click **Run workflow** → **Run workflow**
4. Wait 1-2 minutes
5. Check your email (chen.kelvin822@gmail.com)

## ✅ Done!

You'll now receive daily reports at **8 AM ET** automatically.

## What You Get

- Daily email at 8 AM ET
- Tracks 4 competitors: Databricks, Microsoft Fabric, BigQuery, Redshift
- Categorized signals: Product, Partnership, Acquisition, Pricing, Conference
- Beautiful HTML reports
- 100% free (GitHub Actions + SendGrid free tier)

## Need Help?

- Full documentation: [README.md](README.md)
- Detailed setup: [SETUP.md](SETUP.md)
- Check workflow logs in Actions tab

## Troubleshooting

**Email not received?**
- Check spam folder
- Verify sender in SendGrid (Settings → Sender Authentication)
- Check Actions tab for errors

**Workflow failed?**
- Click on the failed run to see error
- Verify GitHub Secrets are set correctly
- Ensure Actions have write permissions
