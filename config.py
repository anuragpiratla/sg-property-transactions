"""Configuration management for property transaction data fetch."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # PostgreSQL Database
    DATABASE_URL = os.getenv('DATABASE_URL')

    # URA API
    URA_ACCESS_KEY = os.getenv('URA_ACCESS_KEY')
    URA_BASE_URL = 'https://www.ura.gov.sg/uraDataService/invokeUraDS'

    # Database tables
    CONDO_TABLE = 'condo_transactions'
    LANDED_TABLE = 'landed_transactions'

    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        required_vars = [
            ('DATABASE_URL', cls.DATABASE_URL),
            ('URA_ACCESS_KEY', cls.URA_ACCESS_KEY),
        ]

        missing = [var_name for var_name, var_value in required_vars if not var_value]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please check your .env file."
            )
