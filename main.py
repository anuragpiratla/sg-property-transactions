"""
Main script to fetch and store property transaction data.

Retrieves condo and landed property transactions from URA API
and stores them in PostgreSQL database.
"""
import argparse
import logging
import sys
from datetime import datetime

from config import Config
from scrapers.ura_scraper import URAScraper
from db.db_client import DatabaseClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_and_store_ura_data(
    scraper: URAScraper,
    db_client: DatabaseClient,
    include_rentals: bool = False
):
    """
    Fetch URA data and store in PostgreSQL database.

    Args:
        scraper: URAScraper instance
        db_client: DatabaseClient instance
        include_rentals: Whether to also fetch rental data
    """
    logger.info("=" * 60)
    logger.info("Starting URA property transaction fetch")
    logger.info("=" * 60)

    try:
        # Fetch all available transactions
        data = scraper.get_all_available_transactions()

        condo_txns = data['condo']
        landed_txns = data['landed']

        # Store condo transactions
        if condo_txns:
            logger.info(f"\nStoring {len(condo_txns)} condo transactions...")
            condo_inserted = db_client.insert_transactions(
                Config.CONDO_TABLE,
                condo_txns
            )
            logger.info(f"* Successfully stored {condo_inserted} condo transactions")
        else:
            logger.warning("No condo transactions to store")

        # Store landed transactions
        if landed_txns:
            logger.info(f"\nStoring {len(landed_txns)} landed transactions...")
            landed_inserted = db_client.insert_transactions(
                Config.LANDED_TABLE,
                landed_txns
            )
            logger.info(f"* Successfully stored {landed_inserted} landed transactions")
        else:
            logger.warning("No landed transactions to store")

        # Optionally fetch rental data
        if include_rentals:
            logger.info("\nFetching rental data...")
            all_rentals = []
            for batch in range(1, 5):
                rentals = scraper.get_rental_transactions(batch)
                all_rentals.extend(rentals)

            if all_rentals:
                logger.info(f"Storing {len(all_rentals)} rental transactions...")
                logger.info("Note: Rental data storage not implemented. "
                           "Create a rentals table if needed.")

        logger.info("\n" + "=" * 60)
        logger.info("Fetch completed successfully")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error during fetch: {e}", exc_info=True)
        raise


def show_statistics(db_client: DatabaseClient):
    """
    Show statistics about stored data.

    Args:
        db_client: DatabaseClient instance
    """
    logger.info("\n" + "=" * 60)
    logger.info("Database Statistics")
    logger.info("=" * 60)

    try:
        # Condo stats
        condo_count = db_client.get_transaction_count(Config.CONDO_TABLE)
        condo_latest = db_client.get_latest_transaction_date(Config.CONDO_TABLE)

        logger.info(f"\nCondo Transactions:")
        logger.info(f"  Total records: {condo_count}")
        logger.info(f"  Latest transaction: {condo_latest or 'N/A'}")

        # Landed stats
        landed_count = db_client.get_transaction_count(Config.LANDED_TABLE)
        landed_latest = db_client.get_latest_transaction_date(Config.LANDED_TABLE)

        logger.info(f"\nLanded Property Transactions:")
        logger.info(f"  Total records: {landed_count}")
        logger.info(f"  Latest transaction: {landed_latest or 'N/A'}")

        logger.info("\n" + "=" * 60)

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fetch Singapore property transaction data'
    )
    parser.add_argument(
        '--include-rentals',
        action='store_true',
        help='Also fetch rental transaction data'
    )
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Only show database statistics, do not fetch new data'
    )

    args = parser.parse_args()

    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Config.validate()
        logger.info("* Configuration valid")

        # Initialize clients
        logger.info("Initializing API clients...")
        scraper = URAScraper(
            access_key=Config.URA_ACCESS_KEY,
            base_url=Config.URA_BASE_URL
        )

        db_client = DatabaseClient(
            database_url=Config.DATABASE_URL
        )
        logger.info("* Clients initialized")

        if args.stats_only:
            show_statistics(db_client)
        else:
            scrape_and_store_ura_data(
                scraper,
                db_client,
                include_rentals=args.include_rentals
            )

            show_statistics(db_client)

        # Close database connection
        db_client.close()

        logger.info("\n* All operations completed successfully")
        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
