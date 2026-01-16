# Snowflake Competitive Intelligence Monitor

Automated daily monitoring tool that tracks competitive landscape signals across Databricks, Microsoft Fabric, Google BigQuery, and Amazon Redshift.

## Features

- 🤖 **Automated Daily Reports** - Delivered to your inbox every morning at 8 AM ET
- 📊 **Multi-Source Collection** - Aggregates from multiple channels:
  - Company RSS feeds (competitor blogs, newsrooms)
  - HackerNews API (discussions, launches, Show HN)
  - Tech news RSS (TechCrunch, VentureBeat, The Verge, etc.)
  - PR Newswire RSS (press releases)
  - NewsAPI (optional - 6,000+ news sources)
- 🎯 **Smart Classification** - Automatically categorizes signals (Product, Partnership, Acquisition, Pricing, Conference)
- 🔄 **Duplicate Detection** - Hash-based deduplication prevents repeated signals
- 📧 **Professional Email Reports** - Beautiful HTML emails with color-coded signal types
- ☁️ **Zero Infrastructure Cost** - Runs on GitHub Actions (completely free)

## Competitors Tracked

| Company | Focus Areas |
|---------|-------------|
| **Databricks** | Delta Lake, Lakehouse, Unity Catalog |
| **Microsoft Fabric** | Azure Synapse, OneLake, Power BI |
| **Google BigQuery** | BigLake, Vertex AI, Looker |
| **Amazon Redshift** | Aurora, Athena, Glue |

## Signal Types

- 🔴 **Acquisition** - M&A announcements
- 🟢 **Partnership** - Strategic alliances and integrations
- 🔵 **Product** - New features, launches, GA releases
- 🟡 **Pricing** - Price changes, new tiers
- 🟣 **Conference** - Keynotes, speaking events
- ⚪ **General** - Other announcements

## Quick Start

### Prerequisites

- Python 3.10+
- GitHub account (for deployment)
- SendGrid account (free tier)

### 1. Get SendGrid API Key

1. Sign up at [sendgrid.com](https://sendgrid.com) (free tier: 100 emails/day)
2. Navigate to Settings → API Keys
3. Create a new API key with "Mail Send" permissions
4. Save the key securely (you'll need it for GitHub Secrets)

### 2. Create GitHub Repository

```bash
# Create a new private repository on GitHub
# Name it: snowflake-ci-monitor

# Clone this code
git clone <your-repo-url>
cd snowflake-ci-monitor
```

### 3. Configure GitHub Secrets

Go to your repository on GitHub:

1. Navigate to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:
   - Name: `SENDGRID_API_KEY`
   - Value: Your SendGrid API key from step 1
3. Click **New repository secret** again and add:
   - Name: `RECIPIENT_EMAIL`
   - Value: `chen.kelvin822@gmail.com`
4. **(Optional)** For NewsAPI integration, add:
   - Name: `NEWSAPI_KEY`
   - Value: Your NewsAPI key (see [NEWSAPI_SETUP.md](NEWSAPI_SETUP.md) for instructions)

### 4. Test Locally (Optional)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "SENDGRID_API_KEY=your_key_here" > .env
echo "RECIPIENT_EMAIL=chen.kelvin822@gmail.com" >> .env

# Initialize database
python main.py --init

# Send test email
python main.py --test

# Run full pipeline
python main.py
```

### 5. Deploy to GitHub

```bash
# Push code to GitHub
git add .
git commit -m "Initial CI monitor setup"
git push origin main
```

### 6. Verify Deployment

1. Go to **Actions** tab in your GitHub repository
2. You should see the workflow listed
3. Click **Run workflow** to trigger manually (or wait for 8 AM ET)
4. Check your email inbox for the report

## Usage

### Manual Trigger

Run the workflow manually from the GitHub Actions tab:
1. Go to **Actions** → **Daily Competitive Intelligence Monitor**
2. Click **Run workflow** → **Run workflow**

### Scheduled Runs

The workflow automatically runs daily at:
- **8:00 AM ET** (12:00 PM UTC)

### Checking Logs

View execution logs in the Actions tab:
1. Click on a workflow run
2. Click on the "monitor" job
3. Expand steps to see detailed logs

## Project Structure

```
competitive-intelligence/
├── .github/
│   └── workflows/
│       └── daily-monitor.yml        # GitHub Actions workflow
├── src/
│   ├── config.py                    # Configuration management
│   ├── database.py                  # SQLAlchemy models
│   ├── collectors/
│   │   ├── base.py                  # Base collector class
│   │   ├── rss_collector.py         # RSS feed collector
│   │   └── web_scraper.py           # Web scraping (fallback)
│   ├── processors/
│   │   ├── signal_classifier.py     # Signal classification
│   │   └── deduplicator.py          # Duplicate removal
│   └── reporting/
│       ├── report_generator.py      # HTML report generation
│       └── email_sender.py          # SendGrid integration
├── data/
│   └── intelligence.db              # SQLite database (auto-created)
├── config/
│   └── competitors.json             # Competitor definitions
├── templates/
│   └── email_template.html          # Email HTML template
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Configuration

### Modifying Competitors

Edit `config/competitors.json` to add/remove competitors:

```json
{
  "competitors": [
    {
      "name": "New Competitor",
      "domain": "competitor.com",
      "rss_feeds": ["https://competitor.com/blog/feed"],
      "twitter": "@competitor",
      "keywords": ["keyword1", "keyword2"]
    }
  ]
}
```

### Adjusting Schedule

Edit `.github/workflows/daily-monitor.yml`:

```yaml
schedule:
  - cron: '0 14 * * *'  # 10 AM ET (14:00 UTC)
```

### Changing Keywords

Edit `src/config.py` → `signal_keywords` dict to adjust classification keywords.

## Troubleshooting

### Email Not Received

1. **Check spam folder** - First time emails may go to spam
2. **Verify SendGrid API key** - Ensure it has "Mail Send" permissions
3. **Check workflow logs** - Look for error messages in Actions tab
4. **Verify sender authentication** - SendGrid may require sender verification

### Workflow Failed

1. **View logs** in Actions tab
2. **Common issues**:
   - Missing GitHub Secrets
   - Invalid SendGrid API key
   - RSS feed unavailable
   - Rate limiting

### No Signals Collected

1. **Check lookback period** - Default is 24 hours
2. **Verify RSS feeds** - Some competitors may have moved their feeds
3. **Check database** - Run `python main.py` locally to see collection logs

## Maintenance

### Weekly Tasks
- Check GitHub Actions tab for any failed runs
- Review email reports for quality

### Monthly Tasks
- Review signal classification accuracy
- Update keywords if needed
- Check for new RSS feeds from competitors

## Future Enhancements

- Twitter/X API integration for real-time monitoring
- HackerNews integration for community discussions
- NewsAPI integration for broader news coverage
- Web dashboard for historical signal viewing
- AI-powered summarization with GPT-4
- Slack/Teams notifications
- Mobile app for push notifications

## Cost

**Total Monthly Cost: $0**

- GitHub Actions: Free (unlimited for private repos)
- SendGrid: Free tier (100 emails/day, only need 1/day)
- Storage: Free (SQLite in repo)

## Support

For issues or questions:
- Check the [SETUP.md](SETUP.md) guide
- Review workflow logs in Actions tab
- Verify configuration in `config/` directory

## License

Private internal tool for Snowflake Corporate BD team.
