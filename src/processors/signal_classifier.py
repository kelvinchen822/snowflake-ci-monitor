"""Signal classification based on keywords"""

from typing import Dict, List


class SignalClassifier:
    """Classify signals based on keyword matching"""

    def __init__(self, keywords: Dict[str, List[str]]):
        """
        Initialize classifier with keyword mappings.

        Args:
            keywords: Dict mapping signal types to keyword lists
        """
        self.keywords = keywords
        # Define priority order (higher priority checked first)
        self.priority_order = ['acquisition', 'partnership', 'product', 'pricing', 'conference']

    def classify(self, title: str, description: str = '') -> str:
        """
        Classify signal based on title and description.

        Args:
            title: Signal title
            description: Signal description

        Returns:
            Signal type ('acquisition', 'partnership', 'product', 'pricing', 'conference', or 'general')
        """
        # Combine title and description for matching
        text = f"{title} {description}".lower()

        # Check keywords in priority order
        for signal_type in self.priority_order:
            keywords = self.keywords.get(signal_type, [])
            for keyword in keywords:
                if keyword.lower() in text:
                    return signal_type

        # Default to 'general' if no match
        return 'general'

    def classify_batch(self, signals: List[Dict]) -> List[Dict]:
        """
        Classify multiple signals.

        Args:
            signals: List of signal dictionaries

        Returns:
            List of signals with 'signal_type' added
        """
        for signal in signals:
            signal['signal_type'] = self.classify(
                signal.get('title', ''),
                signal.get('description', '')
            )

        return signals

    def get_stats(self, signals: List[Dict]) -> Dict[str, int]:
        """Get classification statistics"""
        stats = {}
        for signal in signals:
            signal_type = signal.get('signal_type', 'general')
            stats[signal_type] = stats.get(signal_type, 0) + 1

        return stats


def test_classifier():
    """Test the signal classifier"""
    from src.config import config

    classifier = SignalClassifier(config.signal_keywords)

    test_signals = [
        {'title': 'Databricks Announces Acquisition of MosaicML', 'description': 'Leading AI company acquired'},
        {'title': 'Microsoft Fabric Partners with Snowflake', 'description': 'New integration partnership'},
        {'title': 'BigQuery Launches New ML Features', 'description': 'GA release of AutoML'},
        {'title': 'Redshift Announces New Pricing Model', 'description': 'Reduced costs for compute'},
        {'title': 'AWS CEO Keynote at re:Invent', 'description': 'Speaking at annual conference'},
        {'title': 'Company Updates Q4 Results', 'description': 'Financial results announced'}
    ]

    classified = classifier.classify_batch(test_signals)

    print("\nClassification Results:")
    for signal in classified:
        print(f"{signal['signal_type'].upper():15} | {signal['title']}")

    print("\nStatistics:")
    stats = classifier.get_stats(classified)
    for signal_type, count in stats.items():
        print(f"  {signal_type}: {count}")


if __name__ == '__main__':
    test_classifier()
