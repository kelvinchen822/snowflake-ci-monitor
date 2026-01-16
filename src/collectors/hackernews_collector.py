"""HackerNews collector using Algolia API"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
from .base import BaseCollector


class HackerNewsCollector(BaseCollector):
    """Collect signals from HackerNews using Algolia API"""

    def __init__(self, competitor_name: str, keywords: List[str], lookback_days: int = 1):
        """
        Initialize HackerNews collector

        Args:
            competitor_name: Name of competitor
            keywords: Keywords to search for
            lookback_days: Number of days to look back
        """
        super().__init__(
            source_url='https://hn.algolia.com/api/v1',
            source_type='hackernews',
            competitor_name=competitor_name
        )
        self.keywords = keywords
        self.lookback_days = lookback_days
        self.api_url = 'https://hn.algolia.com/api/v1/search'

    def collect(self) -> List[Dict]:
        """
        Collect HackerNews posts mentioning competitor keywords

        Returns:
            List of signal dictionaries
        """
        all_signals = []

        # Calculate timestamp for lookback period
        cutoff_date = datetime.utcnow() - timedelta(days=self.lookback_days)
        cutoff_timestamp = int(cutoff_date.timestamp())

        # Search for each keyword
        for keyword in self.keywords:
            try:
                signals = self._search_keyword(keyword, cutoff_timestamp)
                all_signals.extend(signals)
                self.logger.info(f"Found {len(signals)} HN posts for keyword: {keyword}")
            except Exception as e:
                self.logger.error(f"Error searching HN for keyword '{keyword}': {e}")
                continue

        # Deduplicate by URL
        seen_urls = set()
        unique_signals = []
        for signal in all_signals:
            url = signal.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_signals.append(signal)

        self.logger.info(f"Collected {len(unique_signals)} unique HN signals for {self.competitor_name}")
        return unique_signals

    def _search_keyword(self, keyword: str, cutoff_timestamp: int) -> List[Dict]:
        """
        Search HackerNews for a specific keyword

        Args:
            keyword: Search term
            cutoff_timestamp: Unix timestamp for cutoff date

        Returns:
            List of signal dictionaries
        """
        params = {
            'query': keyword,
            'tags': 'story',  # Only get stories, not comments
            'numericFilters': f'created_at_i>{cutoff_timestamp}',
            'hitsPerPage': 20
        }

        response = requests.get(self.api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        signals = []
        for hit in data.get('hits', []):
            # Use story URL if available, otherwise use HN discussion URL
            story_url = hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"

            # Parse created_at timestamp
            created_at = hit.get('created_at_i')
            if created_at:
                published_date = datetime.utcfromtimestamp(created_at)
            else:
                published_date = datetime.utcnow()

            signal = {
                'title': hit.get('title', ''),
                'description': hit.get('story_text', '') or f"HackerNews discussion with {hit.get('points', 0)} points and {hit.get('num_comments', 0)} comments",
                'url': story_url,
                'published_date': published_date,
                'source_type': 'hackernews',
                'source_url': f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                'competitor_name': self.competitor_name,
                'hn_points': hit.get('points', 0),
                'hn_comments': hit.get('num_comments', 0)
            }

            signals.append(signal)

        return signals
