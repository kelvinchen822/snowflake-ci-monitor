"""Configuration management"""

import os
import json
from typing import List, Dict
from pathlib import Path


class Config:
    """Application configuration"""

    def __init__(self):
        # Base paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.config_dir = self.base_dir / 'config'
        self.templates_dir = self.base_dir / 'templates'

        # Database
        self.database_url = os.getenv('DATABASE_URL', f'sqlite:///{self.data_dir}/intelligence.db')

        # Email settings
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL', 'chen.kelvin822@gmail.com')
        self.sender_email = os.getenv('SENDER_EMAIL', 'noreply@snowflake-ci.com')
        self.sender_name = os.getenv('SENDER_NAME', 'Snowflake CI Monitor')

        # Collection settings
        self.lookback_days = int(os.getenv('LOOKBACK_DAYS', '1'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '2'))

        # Signal classification keywords
        self.signal_keywords = {
            'acquisition': [
                'acquire', 'acquisition', 'acquires', 'acquired',
                'merger', 'merge', 'bought', 'purchase', 'buy',
                'announces acquisition'
            ],
            'partnership': [
                'partnership', 'partner', 'integration', 'alliance',
                'collaborate', 'collaboration', 'joint', 'team up',
                'work with', 'teams up', 'announces partnership'
            ],
            'product': [
                'launch', 'release', 'announce', 'introducing',
                'available', 'GA', 'general availability', 'beta',
                'preview', 'feature', 'deprecate', 'sunset', 'unveil',
                'announces', 'new feature'
            ],
            'pricing': [
                'pricing', 'price', 'tier', 'plan', 'cost',
                'free', 'discount', 'savings', 'billing',
                'announces pricing', 'price change'
            ],
            'conference': [
                'keynote', 'conference', 'summit', 'event',
                'speaking', 'present', 'demo', 'talk',
                'presents at', 'speaking at'
            ]
        }

        # Load competitors
        self.competitors = self._load_competitors()

    def _load_competitors(self) -> List[Dict]:
        """Load competitor definitions from JSON"""
        competitors_file = self.config_dir / 'competitors.json'

        if not competitors_file.exists():
            # Return default competitors if file doesn't exist
            return self._get_default_competitors()

        with open(competitors_file, 'r') as f:
            data = json.load(f)
            return data.get('competitors', [])

    def _get_default_competitors(self) -> List[Dict]:
        """Get default competitor list"""
        return [
            {
                "name": "Databricks",
                "domain": "databricks.com",
                "rss_feeds": ["https://www.databricks.com/blog/feed"],
                "twitter": "@databricks",
                "keywords": ["Databricks", "Delta Lake", "lakehouse"]
            },
            {
                "name": "Microsoft Fabric",
                "domain": "microsoft.com",
                "rss_feeds": ["https://azure.microsoft.com/en-us/blog/feed/"],
                "twitter": "@Azure",
                "keywords": ["Microsoft Fabric", "Azure Synapse", "OneLake"]
            },
            {
                "name": "Google BigQuery",
                "domain": "cloud.google.com",
                "rss_feeds": ["https://cloud.google.com/blog/feeds/posts.xml"],
                "twitter": "@GoogleCloud",
                "keywords": ["BigQuery", "BigLake", "Vertex AI"]
            },
            {
                "name": "Amazon Redshift",
                "domain": "aws.amazon.com",
                "rss_feeds": ["https://aws.amazon.com/blogs/aws/feed/"],
                "twitter": "@AWSCloud",
                "keywords": ["Redshift", "Aurora", "Athena"]
            }
        ]

    def validate(self) -> bool:
        """Validate required configuration"""
        errors = []

        if not self.sendgrid_api_key:
            errors.append("SENDGRID_API_KEY environment variable not set")

        if not self.recipient_email:
            errors.append("RECIPIENT_EMAIL environment variable not set")

        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True


# Global config instance
config = Config()
