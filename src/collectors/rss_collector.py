"""RSS feed collector"""

import feedparser
from datetime import datetime
from typing import List, Dict
from .base import BaseCollector, retry_on_failure


class RSSCollector(BaseCollector):
    """Collect signals from RSS feeds"""

    def __init__(self, competitor_name: str, feed_url: str, lookback_days: int = 1):
        super().__init__(competitor_name, feed_url)
        self.lookback_days = lookback_days

    @retry_on_failure(max_retries=3, delay=2)
    def collect(self) -> List[Dict]:
        """Collect signals from RSS feed"""
        print(f"Collecting RSS feed for {self.competitor_name}: {self.source_url}")

        try:
            feed = feedparser.parse(self.source_url)

            if feed.bozo:
                # Feed has parsing errors
                print(f"Warning: Feed parsing error for {self.source_url}: {feed.bozo_exception}")

            signals = []
            for entry in feed.entries:
                signal = self._parse_entry(entry)
                if signal:
                    signals.append(signal)

            # Filter by date
            filtered_signals = self.filter_by_date(signals, self.lookback_days)

            print(f"Collected {len(filtered_signals)} signals from {self.competitor_name}")
            return filtered_signals

        except Exception as e:
            print(f"Error collecting RSS feed {self.source_url}: {str(e)}")
            raise

    def _parse_entry(self, entry) -> Dict:
        """Parse a single RSS feed entry"""
        try:
            # Get published date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_date = datetime(*entry.updated_parsed[:6])

            # Get description/summary
            description = ''
            if hasattr(entry, 'summary'):
                description = entry.summary
            elif hasattr(entry, 'description'):
                description = entry.description

            # Clean HTML tags from description
            description = self._clean_html(description)

            signal = {
                'title': entry.get('title', ''),
                'description': description,
                'url': entry.get('link', ''),
                'published_date': published_date,
                'source_type': 'rss',
                'source_url': self.source_url,
                'competitor_name': self.competitor_name
            }

            return self.normalize_signal(signal)

        except Exception as e:
            print(f"Error parsing RSS entry: {str(e)}")
            return None

    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        from bs4 import BeautifulSoup

        if not html_text:
            return ''

        try:
            soup = BeautifulSoup(html_text, 'lxml')
            text = soup.get_text(separator=' ', strip=True)
            # Limit to first 500 characters
            return text[:500] + '...' if len(text) > 500 else text
        except:
            # If parsing fails, return as-is (truncated)
            return html_text[:500]


def test_rss_collector():
    """Test the RSS collector with Databricks feed"""
    collector = RSSCollector(
        competitor_name="Databricks",
        feed_url="https://www.databricks.com/blog/feed",
        lookback_days=7
    )

    signals = collector.collect()
    print(f"\nCollected {len(signals)} signals:")
    for signal in signals[:3]:  # Print first 3
        print(f"\nTitle: {signal['title']}")
        print(f"Date: {signal['published_date']}")
        print(f"URL: {signal['url']}")
        print(f"Description: {signal['description'][:100]}...")


if __name__ == '__main__':
    test_rss_collector()
