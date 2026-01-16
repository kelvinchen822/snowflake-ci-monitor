"""Base collector class with common functionality"""

import time
from functools import wraps
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


def retry_on_failure(max_retries=3, delay=2):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    wait_time = delay * (attempt + 1)
                    print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator


class BaseCollector(ABC):
    """Abstract base class for all collectors"""

    def __init__(self, competitor_name: str, source_url: str):
        self.competitor_name = competitor_name
        self.source_url = source_url

    @abstractmethod
    def collect(self) -> List[Dict]:
        """
        Collect signals from the source.

        Returns:
            List of signal dictionaries with keys:
                - title: Signal title
                - description: Signal description
                - url: Link to full content
                - published_date: Publication date (datetime object)
                - source_type: Type of source ('rss', 'web', etc.)
                - source_url: URL of the source
        """
        pass

    def normalize_signal(self, raw_signal: Dict) -> Dict:
        """Normalize signal data to standard format"""
        return {
            'title': raw_signal.get('title', '').strip(),
            'description': raw_signal.get('description', '').strip(),
            'url': raw_signal.get('url', '').strip(),
            'published_date': raw_signal.get('published_date'),
            'source_type': raw_signal.get('source_type', 'unknown'),
            'source_url': self.source_url
        }

    def filter_by_date(self, signals: List[Dict], lookback_days: int = 1) -> List[Dict]:
        """Filter signals to only include recent ones"""
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        filtered = []

        for signal in signals:
            pub_date = signal.get('published_date')
            if pub_date and pub_date >= cutoff_date:
                filtered.append(signal)

        return filtered
