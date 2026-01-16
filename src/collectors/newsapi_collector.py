"""NewsAPI collector for competitor news"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
from .base import BaseCollector


class NewsAPICollector(BaseCollector):
    """Collect news articles from NewsAPI"""

    def __init__(self, api_key: str, competitor_name: str, keywords: List[str], lookback_days: int = 1):
        """
        Initialize NewsAPI collector

        Args:
            api_key: NewsAPI API key
            competitor_name: Name of competitor
            keywords: Keywords to search for
            lookback_days: Number of days to look back
        """
        super().__init__(
            source_url='https://newsapi.org/v2',
            source_type='newsapi',
            competitor_name=competitor_name
        )
        self.api_key = api_key
        self.keywords = keywords
        self.lookback_days = lookback_days
        self.api_url = 'https://newsapi.org/v2/everything'

    def collect(self) -> List[Dict]:
        """
        Collect news articles mentioning competitor keywords

        Returns:
            List of signal dictionaries
        """
        if not self.api_key or self.api_key == 'your_newsapi_key_here':
            self.logger.warning(f"NewsAPI key not configured for {self.competitor_name}, skipping")
            return []

        all_signals = []

        # Calculate date range
        from_date = (datetime.utcnow() - timedelta(days=self.lookback_days)).strftime('%Y-%m-%d')
        to_date = datetime.utcnow().strftime('%Y-%m-%d')

        # Combine keywords into a single query
        query = ' OR '.join(self.keywords)

        try:
            signals = self._search_news(query, from_date, to_date)
            all_signals.extend(signals)
            self.logger.info(f"Found {len(signals)} news articles for {self.competitor_name}")
        except Exception as e:
            self.logger.error(f"Error searching NewsAPI for {self.competitor_name}: {e}")

        return all_signals

    def _search_news(self, query: str, from_date: str, to_date: str) -> List[Dict]:
        """
        Search NewsAPI for articles

        Args:
            query: Search query
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            List of signal dictionaries
        """
        params = {
            'q': query,
            'from': from_date,
            'to': to_date,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 100,  # Max results per request
            'apiKey': self.api_key
        }

        response = requests.get(self.api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('status') != 'ok':
            raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")

        signals = []
        for article in data.get('articles', []):
            # Parse published date
            published_at = article.get('publishedAt')
            if published_at:
                try:
                    published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    published_date = datetime.utcnow()
            else:
                published_date = datetime.utcnow()

            # Use description or content as description
            description = article.get('description', '') or article.get('content', '')

            signal = {
                'title': article.get('title', ''),
                'description': description,
                'url': article.get('url', ''),
                'published_date': published_date,
                'source_type': 'newsapi',
                'source_url': article.get('url', ''),
                'competitor_name': self.competitor_name,
                'news_source': article.get('source', {}).get('name', 'Unknown')
            }

            signals.append(signal)

        return signals
