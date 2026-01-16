"""Signal deduplication"""

import hashlib
from typing import Dict, List


class Deduplicator:
    """Remove duplicate signals based on hash"""

    @staticmethod
    def generate_hash(title: str, url: str, published_date: str) -> str:
        """
        Generate unique hash for a signal.

        Args:
            title: Signal title
            url: Signal URL
            published_date: Publication date (string or datetime)

        Returns:
            SHA256 hash as hex string
        """
        # Convert published_date to string if it's a datetime
        date_str = str(published_date) if published_date else ''

        # Create content string
        content = f"{title}|{url}|{date_str}"

        # Generate hash
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def add_hashes(signals: List[Dict]) -> List[Dict]:
        """
        Add hash to each signal.

        Args:
            signals: List of signal dictionaries

        Returns:
            List of signals with 'hash' field added
        """
        for signal in signals:
            signal['hash'] = Deduplicator.generate_hash(
                signal.get('title', ''),
                signal.get('url', ''),
                signal.get('published_date')
            )

        return signals

    @staticmethod
    def remove_duplicates(signals: List[Dict]) -> List[Dict]:
        """
        Remove duplicate signals from a list (keeps first occurrence).

        Args:
            signals: List of signal dictionaries with 'hash' field

        Returns:
            List of unique signals
        """
        seen_hashes = set()
        unique_signals = []

        for signal in signals:
            signal_hash = signal.get('hash')
            if signal_hash and signal_hash not in seen_hashes:
                seen_hashes.add(signal_hash)
                unique_signals.append(signal)

        removed_count = len(signals) - len(unique_signals)
        if removed_count > 0:
            print(f"Removed {removed_count} duplicate signals")

        return unique_signals

    @staticmethod
    def check_against_database(session, signals: List[Dict]) -> List[Dict]:
        """
        Filter signals that already exist in database.

        Args:
            session: Database session
            signals: List of signal dictionaries with 'hash' field

        Returns:
            List of new signals not in database
        """
        from src.database import Signal

        new_signals = []

        for signal in signals:
            signal_hash = signal.get('hash')
            if not signal_hash:
                continue

            # Check if signal exists
            existing = session.query(Signal).filter_by(hash=signal_hash).first()
            if not existing:
                new_signals.append(signal)

        duplicate_count = len(signals) - len(new_signals)
        if duplicate_count > 0:
            print(f"Filtered {duplicate_count} signals already in database")

        return new_signals


def test_deduplicator():
    """Test the deduplicator"""
    from datetime import datetime

    signals = [
        {'title': 'Test 1', 'url': 'http://example.com/1', 'published_date': datetime(2024, 1, 1)},
        {'title': 'Test 2', 'url': 'http://example.com/2', 'published_date': datetime(2024, 1, 2)},
        {'title': 'Test 1', 'url': 'http://example.com/1', 'published_date': datetime(2024, 1, 1)},  # Duplicate
        {'title': 'Test 3', 'url': 'http://example.com/3', 'published_date': datetime(2024, 1, 3)},
    ]

    # Add hashes
    signals_with_hashes = Deduplicator.add_hashes(signals)

    print(f"Original signals: {len(signals_with_hashes)}")
    for signal in signals_with_hashes:
        print(f"  {signal['title']}: {signal['hash'][:16]}...")

    # Remove duplicates
    unique_signals = Deduplicator.remove_duplicates(signals_with_hashes)

    print(f"\nUnique signals: {len(unique_signals)}")
    for signal in unique_signals:
        print(f"  {signal['title']}: {signal['hash'][:16]}...")


if __name__ == '__main__':
    test_deduplicator()
