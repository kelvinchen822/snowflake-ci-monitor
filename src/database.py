"""Database models and operations using SQLAlchemy"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import Optional, List

Base = declarative_base()


class Competitor(Base):
    """Competitor company model"""
    __tablename__ = 'competitors'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255))
    twitter_handle = Column(String(100))

    # Relationships
    signal_sources = relationship("SignalSource", back_populates="competitor")
    signals = relationship("Signal", back_populates="competitor")

    def __repr__(self):
        return f"<Competitor(id={self.id}, name='{self.name}')>"


class SignalSource(Base):
    """Signal source (RSS feed, API endpoint, etc.)"""
    __tablename__ = 'signal_sources'

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('competitors.id'))
    type = Column(String(50))  # 'rss', 'twitter', 'web', 'news'
    url = Column(Text)
    last_checked = Column(DateTime)

    # Relationships
    competitor = relationship("Competitor", back_populates="signal_sources")

    def __repr__(self):
        return f"<SignalSource(id={self.id}, type='{self.type}', url='{self.url}')>"


class Signal(Base):
    """Competitive intelligence signal"""
    __tablename__ = 'signals'

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('competitors.id'))
    signal_type = Column(String(50))  # 'product', 'partnership', 'acquisition', 'pricing', 'conference', 'general'
    title = Column(Text, nullable=False)
    description = Column(Text)
    url = Column(Text)
    published_date = Column(DateTime)
    discovered_date = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String(50))  # 'rss', 'twitter', 'web', etc.
    source_url = Column(Text)
    hash = Column(String(64), unique=True)  # For deduplication

    # Relationships
    competitor = relationship("Competitor", back_populates="signals")

    def __repr__(self):
        return f"<Signal(id={self.id}, type='{self.signal_type}', title='{self.title[:50]}...')>"


class ProcessingLog(Base):
    """Log of monitoring pipeline executions"""
    __tablename__ = 'processing_log'

    id = Column(Integer, primary_key=True)
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    signals_collected = Column(Integer)
    errors = Column(Text)
    duration_seconds = Column(Float)

    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, timestamp={self.run_timestamp}, signals={self.signals_collected})>"


class Database:
    """Database manager class"""

    def __init__(self, db_url: str = None):
        """Initialize database connection"""
        if db_url is None:
            # Default to SQLite in data directory
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'intelligence.db')
            db_url = f'sqlite:///{db_path}'

        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def init_db(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        print("Database tables created successfully")

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def seed_competitors(self, competitors_data: List[dict]):
        """Seed competitor data into database"""
        session = self.get_session()
        try:
            for comp_data in competitors_data:
                # Check if competitor already exists
                existing = session.query(Competitor).filter_by(name=comp_data['name']).first()
                if not existing:
                    competitor = Competitor(
                        name=comp_data['name'],
                        domain=comp_data.get('domain'),
                        twitter_handle=comp_data.get('twitter')
                    )
                    session.add(competitor)

                    # Add RSS feeds as signal sources
                    for feed_url in comp_data.get('rss_feeds', []):
                        source = SignalSource(
                            competitor=competitor,
                            type='rss',
                            url=feed_url
                        )
                        session.add(source)

            session.commit()
            print("Competitor data seeded successfully")
        except Exception as e:
            session.rollback()
            print(f"Error seeding competitors: {e}")
            raise
        finally:
            session.close()

    def add_signal(self, session, signal_data: dict) -> Optional[Signal]:
        """Add a signal to the database if not duplicate"""
        signal_hash = signal_data.get('hash')

        # Check for duplicate
        existing = session.query(Signal).filter_by(hash=signal_hash).first()
        if existing:
            return None

        signal = Signal(**signal_data)
        session.add(signal)
        return signal

    def get_recent_signals(self, hours: int = 24) -> List[Signal]:
        """Get signals from the last N hours"""
        from sqlalchemy.orm import joinedload

        session = self.get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            signals = session.query(Signal).options(
                joinedload(Signal.competitor)
            ).filter(
                Signal.discovered_date >= cutoff
            ).order_by(Signal.discovered_date.desc()).all()

            # Expunge signals from session so they can be used after session closes
            for signal in signals:
                session.expunge(signal)

            return signals
        finally:
            session.close()

    def log_processing_run(self, signals_count: int, errors: Optional[str], duration: float):
        """Log a processing run"""
        session = self.get_session()
        try:
            log = ProcessingLog(
                signals_collected=signals_count,
                errors=errors,
                duration_seconds=duration
            )
            session.add(log)
            session.commit()
        finally:
            session.close()


# Import timedelta for get_recent_signals
from datetime import timedelta
