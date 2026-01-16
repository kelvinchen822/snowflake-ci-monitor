# NewsAPI Setup Guide

NewsAPI provides access to thousands of news sources and articles. The free tier includes 100 requests per day, which is sufficient for daily competitive intelligence monitoring.

## Step 1: Create Free NewsAPI Account

1. Go to https://newsapi.org/register
2. Fill out the registration form:
   - Email: chen.kelvin822@gmail.com
   - Choose "Free" plan (100 requests/day)
3. Verify your email address
4. You'll receive your API key immediately

## Step 2: Get Your API Key

1. Log in to https://newsapi.org/account
2. Your API key will be displayed on the dashboard
3. It looks like: `1234567890abcdef1234567890abcdef`

## Step 3: Add API Key to GitHub Secrets

1. Go to your GitHub repository: https://github.com/kelvinchen822/snowflake-ci-monitor
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `NEWSAPI_KEY`
5. Value: [paste your API key here]
6. Click **Add secret**

## Step 4: Test the Integration

Once you've added the secret, the next workflow run will automatically use NewsAPI to collect news articles about your competitors.

You can manually trigger a test run:
1. Go to **Actions** tab
2. Click **Daily Competitive Intelligence Monitor**
3. Click **Run workflow** → **Run workflow**
4. Check the logs to see NewsAPI collection results

## What NewsAPI Provides

NewsAPI searches thousands of news sources including:
- TechCrunch, VentureBeat, Wired, Ars Technica
- Business publications: Bloomberg, Reuters, WSJ
- General news: CNN, BBC, The Guardian

For each competitor, it searches for articles mentioning their keywords:
- **Databricks**: "Databricks", "Delta Lake", "lakehouse", "Unity Catalog", "MLflow"
- **Microsoft Fabric**: "Fabric", "Synapse", "OneLake", "Power BI", "Azure Data"
- **Google BigQuery**: "BigQuery", "BigLake", "Vertex", "Looker", "Dataform"
- **Amazon Redshift**: "Redshift", "Aurora", "Athena", "Glue", "data warehouse"

## Free Tier Limits

- **100 requests per day**
- Each competitor search = 1 request
- With 4 competitors, you'll use 4 requests per day
- Plenty of headroom for the free tier

## Optional: Local Testing

If you want to test NewsAPI locally:

1. Create or update `.env` file:
   ```
   NEWSAPI_KEY=your_api_key_here
   ```

2. Run the monitor:
   ```bash
   python main.py
   ```

3. Check the output for NewsAPI collection results

## Troubleshooting

**Error: "NewsAPI not configured"**
- Make sure you've added `NEWSAPI_KEY` to GitHub Secrets
- Verify the secret name is exactly `NEWSAPI_KEY` (case-sensitive)

**Error: "HTTP 401: Unauthorized"**
- Check that your API key is valid
- Verify you haven't exceeded the 100 requests/day limit
- Make sure the API key is pasted correctly (no extra spaces)

**Error: "HTTP 429: Too Many Requests"**
- You've exceeded the free tier limit (100 requests/day)
- Wait until the next day (limits reset at midnight UTC)
- Consider reducing the number of competitors or search frequency

## Cost

**Free Tier**: $0/month
- 100 requests/day
- Perfect for 4 competitors with daily monitoring

**Developer Plan**: $449/month
- 250,000 requests/month
- Only needed for much larger scale monitoring
