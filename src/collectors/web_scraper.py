"""Web scraper for sources without RSS feeds"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from .base import BaseCollector, retry_on_failure


class WebScraper(BaseCollector):
    """Scrape signals from web pages"""

    def __init__(self, competitor_name: str, page_url: str, lookback_days: int = 1):
        super().__init__(competitor_name, page_url)
        self.lookback_days = lookback_days

    @retry_on_failure(max_retries=3, delay=2)
    def collect(self) -> List[Dict]:
        """Collect signals by scraping web page"""
        print(f"Scraping web page for {self.competitor_name}: {self.source_url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.source_url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Generic scraping logic - may need customization per site
            signals = self._extract_signals(soup)

            # Filter by date
            filtered_signals = self.filter_by_date(signals, self.lookback_days)

            print(f"Scraped {len(filtered_signals)} signals from {self.competitor_name}")
            return filtered_signals

        except Exception as e:
            print(f"Error scraping {self.source_url}: {str(e)}")
            raise

    def _extract_signals(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract signals from parsed HTML.
        This is a generic implementation that looks for common blog/news patterns.
        May need customization for specific sites.
        """
        signals = []

        # Try to find article/post elements (common patterns)
        articles = soup.find_all(['article', 'div'], class_=lambda c: c and any(
            x in str(c).lower() for x in ['post', 'article', 'blog', 'news', 'item']
        ))

        for article in articles[:20]:  # Limit to first 20
            signal = self._parse_article(article)
            if signal:
                signals.append(signal)

        return signals

    def _parse_article(self, article) -> Dict:
        """Parse a single article element"""
        try:
            # Find title (h1, h2, h3, or a with title-like class)
            title_elem = article.find(['h1', 'h2', 'h3', 'a'], class_=lambda c: c and 'title' in str(c).lower())
            if not title_elem:
                title_elem = article.find(['h1', 'h2', 'h3'])

            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            # Find link
            link = ''
            if title_elem.name == 'a':
                link = title_elem.get('href', '')
            else:
                link_elem = article.find('a')
                if link_elem:
                    link = link_elem.get('href', '')

            # Make link absolute if relative
            if link and not link.startswith('http'):
                from urllib.parse import urljoin
                link = urljoin(self.source_url, link)

            # Find description
            desc_elem = article.find(['p', 'div'], class_=lambda c: c and any(
                x in str(c).lower() for x in ['summary', 'excerpt', 'description', 'content']
            ))
            description = desc_elem.get_text(strip=True)[:500] if desc_elem else ''

            # Find date (this is tricky, may not always work)
            date_elem = article.find(['time', 'span'], class_=lambda c: c and 'date' in str(c).lower())
            published_date = None
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                published_date = self._parse_date(date_str)

            if not published_date:
                # Use current date as fallback
                published_date = datetime.now()

            signal = {
                'title': title,
                'description': description,
                'url': link,
                'published_date': published_date,
                'source_type': 'web',
                'source_url': self.source_url
            }

            return self.normalize_signal(signal)

        except Exception as e:
            print(f"Error parsing article: {str(e)}")
            return None

    def _parse_date(self, date_str: str) -> datetime:
        """Attempt to parse a date string"""
        from dateutil import parser

        try:
            return parser.parse(date_str)
        except:
            return None


if __name__ == '__main__':
    # Test scraper
    scraper = WebScraper(
        competitor_name="Test",
        page_url="https://www.databricks.com/blog",
        lookback_days=7
    )
    signals = scraper.collect()
    print(f"\nScraped {len(signals)} signals")
    for signal in signals[:2]:
        print(f"\nTitle: {signal['title']}")
        print(f"URL: {signal['url']}")
