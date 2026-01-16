"""Generate HTML reports from signals"""

from datetime import datetime, timedelta
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


class ReportGenerator:
    """Generate HTML email reports"""

    def __init__(self, template_dir: Path = None):
        """Initialize report generator with template directory"""
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / 'templates'

        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.template = self.env.get_template('email_template.html')

    def generate(self, signals: List, hours: int = 24) -> str:
        """
        Generate HTML report from signals.

        Args:
            signals: List of Signal objects from database
            hours: Number of hours to include in date range

        Returns:
            HTML string
        """
        # Group signals by competitor
        grouped = self._group_by_competitor(signals)

        # Get statistics
        stats = self._get_stats(signals)

        # Generate date range string
        date_range = self._get_date_range(hours)

        # Render template
        html = self.template.render(
            grouped_signals=grouped,
            stats=stats,
            date_range=date_range,
            total_signals=len(signals)
        )

        return html

    def _group_by_competitor(self, signals: List) -> Dict[str, List]:
        """Group signals by competitor name"""
        grouped = {}

        for signal in signals:
            competitor_name = signal.competitor.name if signal.competitor else 'Unknown'

            if competitor_name not in grouped:
                grouped[competitor_name] = []

            # Convert signal to dict for template
            signal_dict = {
                'title': signal.title,
                'description': signal.description,
                'url': signal.url,
                'signal_type': signal.signal_type,
                'published_date': signal.published_date,
                'discovered_date': signal.discovered_date
            }
            grouped[competitor_name].append(signal_dict)

        # Sort signals within each competitor by date (newest first)
        for competitor in grouped:
            grouped[competitor].sort(
                key=lambda x: x['published_date'] or x['discovered_date'],
                reverse=True
            )

        return grouped

    def _get_stats(self, signals: List) -> Dict[str, int]:
        """Get signal type statistics"""
        stats = {}

        for signal in signals:
            signal_type = signal.signal_type
            stats[signal_type] = stats.get(signal_type, 0) + 1

        return stats

    def _get_date_range(self, hours: int) -> str:
        """Generate date range string"""
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)

        if hours == 24:
            return f"Last 24 Hours · {end_date.strftime('%B %d, %Y')}"
        else:
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"

    def generate_test_report(self) -> str:
        """Generate a test report with sample data"""
        from datetime import datetime

        # Create mock signals
        class MockCompetitor:
            def __init__(self, name):
                self.name = name

        class MockSignal:
            def __init__(self, competitor_name, title, signal_type, description=''):
                self.competitor = MockCompetitor(competitor_name)
                self.title = title
                self.description = description
                self.url = 'https://example.com'
                self.signal_type = signal_type
                self.published_date = datetime.now()
                self.discovered_date = datetime.now()

        mock_signals = [
            MockSignal('Databricks', 'Databricks Launches New Delta Lake Features', 'product',
                      'Introducing enhanced performance and data reliability features'),
            MockSignal('Databricks', 'Databricks Partners with Tableau', 'partnership',
                      'New integration for seamless data analytics'),
            MockSignal('Microsoft Fabric', 'OneLake Now Generally Available', 'product',
                      'Microsoft\'s unified data lake solution reaches GA'),
            MockSignal('Google BigQuery', 'BigQuery Announces Price Reduction', 'pricing',
                      'Reduced costs for compute-intensive workloads'),
            MockSignal('Amazon Redshift', 'AWS CEO Keynote at re:Invent', 'conference',
                      'Announcing new Redshift capabilities'),
        ]

        return self.generate(mock_signals, hours=24)


def test_report_generator():
    """Test the report generator"""
    generator = ReportGenerator()
    html = generator.generate_test_report()

    # Save to file
    output_path = Path(__file__).parent.parent.parent / 'test_report.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Test report generated: {output_path}")


if __name__ == '__main__':
    test_report_generator()
