"""Main entry point for Competitive Intelligence Monitor"""

import sys
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from src.database import Database
from src.collectors.rss_collector import RSSCollector
from src.processors.signal_classifier import SignalClassifier
from src.processors.deduplicator import Deduplicator
from src.reporting.report_generator import ReportGenerator
from src.reporting.email_sender import EmailSender


class CIMonitor:
    """Main CI monitoring pipeline"""

    def __init__(self):
        self.db = Database(config.database_url)
        self.classifier = SignalClassifier(config.signal_keywords)
        self.report_generator = ReportGenerator()
        self.email_sender = None

        # Initialize email sender if API key is available
        if config.sendgrid_api_key:
            self.email_sender = EmailSender(
                api_key=config.sendgrid_api_key,
                sender_email=config.sender_email,
                sender_name=config.sender_name
            )

    def initialize_database(self):
        """Initialize database and seed competitor data"""
        print("Initializing database...")
        self.db.init_db()
        self.db.seed_competitors(config.competitors)
        print("✓ Database initialized successfully")

    def collect_signals(self) -> list:
        """Collect signals from all sources"""
        print("\n" + "="*60)
        print("COLLECTING SIGNALS")
        print("="*60)

        all_signals = []
        session = self.db.get_session()

        try:
            # Get all RSS feeds from database
            from src.database import SignalSource, Competitor

            sources = session.query(SignalSource).filter_by(type='rss').all()

            for source in sources:
                try:
                    competitor_name = source.competitor.name
                    collector = RSSCollector(
                        competitor_name=competitor_name,
                        feed_url=source.url,
                        lookback_days=config.lookback_days
                    )

                    signals = collector.collect()
                    all_signals.extend(signals)

                    # Update last_checked timestamp
                    source.last_checked = datetime.utcnow()
                    session.commit()

                except Exception as e:
                    print(f"✗ Error collecting from {source.url}: {str(e)}")
                    continue

            print(f"\n✓ Total signals collected: {len(all_signals)}")
            return all_signals

        finally:
            session.close()

    def process_signals(self, signals: list) -> list:
        """Process and store signals"""
        print("\n" + "="*60)
        print("PROCESSING SIGNALS")
        print("="*60)

        # Add hashes for deduplication
        signals = Deduplicator.add_hashes(signals)

        # Remove duplicates within collected batch
        signals = Deduplicator.remove_duplicates(signals)

        # Classify signals
        signals = self.classifier.classify_batch(signals)

        # Check against database and store new signals
        session = self.db.get_session()
        new_signals = []

        try:
            from src.database import Signal, Competitor

            # Filter out signals already in database
            signals = Deduplicator.check_against_database(session, signals)

            # Store new signals
            for signal_data in signals:
                # Find competitor by name
                competitor_name = signal_data.get('competitor_name', '')

                if not competitor_name:
                    print(f"Warning: No competitor name for signal: {signal_data['title'][:50]}")
                    continue

                competitor = session.query(Competitor).filter_by(name=competitor_name).first()

                if not competitor:
                    print(f"Warning: Could not find competitor '{competitor_name}' for signal: {signal_data['title'][:50]}")
                    continue

                # Filter by keywords - only store signals that mention competitor keywords
                comp_config = next((c for c in config.competitors if c['name'] == competitor_name), None)
                if comp_config:
                    keywords = comp_config.get('keywords', [])
                    text_to_search = f"{signal_data.get('title', '')} {signal_data.get('description', '')}".lower()

                    # Check if any keyword appears in title or description
                    keyword_found = any(keyword.lower() in text_to_search for keyword in keywords)

                    if not keyword_found:
                        # Skip signals that don't match competitor keywords
                        continue

                # Create signal
                signal = Signal(
                    competitor_id=competitor.id,
                    signal_type=signal_data['signal_type'],
                    title=signal_data['title'],
                    description=signal_data['description'],
                    url=signal_data['url'],
                    published_date=signal_data['published_date'],
                    source_type=signal_data['source_type'],
                    source_url=signal_data['source_url'],
                    hash=signal_data['hash']
                )

                session.add(signal)
                new_signals.append(signal)

            session.commit()
            print(f"✓ Stored {len(new_signals)} new signals in database")

            # Print classification stats
            stats = self.classifier.get_stats(signals)
            if stats:
                print("\nSignal Classification:")
                for signal_type, count in sorted(stats.items()):
                    print(f"  {signal_type:15} {count}")

            return new_signals

        except Exception as e:
            session.rollback()
            print(f"✗ Error processing signals: {str(e)}")
            raise
        finally:
            session.close()

    def generate_and_send_report(self, test_mode=False):
        """Generate and send email report"""
        print("\n" + "="*60)
        print("GENERATING REPORT")
        print("="*60)

        # Get recent signals
        if test_mode:
            # Use sample data for test
            html = self.report_generator.generate_test_report()
            subject = "✓ TEST: Competitive Intelligence Digest"
        else:
            signals = self.db.get_recent_signals(hours=24)
            print(f"Found {len(signals)} signals from last 24 hours")

            html = self.report_generator.generate(signals, hours=24)
            subject = f"Competitive Intelligence Digest - {datetime.now().strftime('%B %d, %Y')}"

        # Send email
        if self.email_sender:
            print("\nSending email...")
            success = self.email_sender.send_report(
                recipient_email=config.recipient_email,
                subject=subject,
                html_content=html
            )

            if success:
                print("✓ Report sent successfully")
            else:
                print("✗ Failed to send report")
                return False
        else:
            print("✗ Email sender not configured (missing SENDGRID_API_KEY)")
            return False

        return True

    def run(self, test_mode=False):
        """Run the complete monitoring pipeline"""
        start_time = time.time()
        errors = []

        try:
            print("\n" + "="*60)
            print("SNOWFLAKE COMPETITIVE INTELLIGENCE MONITOR")
            print("="*60)
            print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Validate configuration
            if not config.validate():
                print("\n✗ Configuration validation failed")
                return False

            # Auto-initialize database if it doesn't exist
            db_path = Path(config.data_dir) / 'intelligence.db'
            if not db_path.exists():
                print("\n✓ Database not found, initializing automatically...")
                self.initialize_database()

            if not test_mode:
                # Collect signals
                signals = self.collect_signals()

                # Process and store
                new_signals = self.process_signals(signals)

            # Generate and send report
            success = self.generate_and_send_report(test_mode=test_mode)

            # Log execution
            duration = time.time() - start_time
            error_text = None if success else "Failed to send report"

            if not test_mode:
                self.db.log_processing_run(
                    signals_count=len(new_signals) if 'new_signals' in locals() else 0,
                    errors=error_text,
                    duration=duration
                )

            print("\n" + "="*60)
            print(f"✓ Pipeline completed in {duration:.2f} seconds")
            print("="*60)

            return success

        except Exception as e:
            duration = time.time() - start_time
            print(f"\n✗ Pipeline failed: {str(e)}")

            # Log error
            self.db.log_processing_run(
                signals_count=0,
                errors=str(e),
                duration=duration
            )

            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Competitive Intelligence Monitor')
    parser.add_argument('--init', action='store_true', help='Initialize database')
    parser.add_argument('--test', action='store_true', help='Send test email with sample data')

    args = parser.parse_args()

    monitor = CIMonitor()

    if args.init:
        # Initialize database only
        monitor.initialize_database()
        return 0

    if args.test:
        # Run in test mode (send test email)
        success = monitor.run(test_mode=True)
        return 0 if success else 1

    # Normal run
    success = monitor.run()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
