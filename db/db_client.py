"""
PostgreSQL client for storing property transaction data.
"""
from typing import List, Dict, Optional
import psycopg2
import psycopg2.extras
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseClient:
    """Client for interacting with PostgreSQL database."""

    def __init__(self, database_url: str):
        """
        Initialize PostgreSQL client.

        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.conn = None
        self.connect()
        logger.info("PostgreSQL client initialized")

    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.conn.autocommit = False
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def insert_transactions(
        self,
        table_name: str,
        transactions: List[Dict],
        batch_size: int = 1000
    ) -> int:
        """
        Insert transactions into database table in batches.

        Args:
            table_name: Name of the table to insert into
            transactions: List of transaction dictionaries
            batch_size: Number of records to insert per batch

        Returns:
            Number of successfully inserted records
        """
        if not transactions:
            logger.warning("No transactions to insert")
            return 0

        total_inserted = 0
        total_batches = (len(transactions) + batch_size - 1) // batch_size

        logger.info(f"Inserting {len(transactions)} records into {table_name} in {total_batches} batches...")

        cursor = self.conn.cursor()

        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            try:
                # Build INSERT query with ON CONFLICT DO NOTHING
                if batch:
                    columns = batch[0].keys()
                    placeholders = ', '.join(['%s'] * len(columns))
                    columns_str = ', '.join(columns)

                    query = f"""
                        INSERT INTO {table_name} ({columns_str})
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING
                    """

                    # Execute batch insert
                    values = [tuple(txn.values()) for txn in batch]
                    psycopg2.extras.execute_batch(cursor, query, values)
                    self.conn.commit()

                    inserted_count = cursor.rowcount
                    total_inserted += inserted_count
                    logger.info(f"Batch {batch_num}/{total_batches}: Inserted {inserted_count} records")

            except psycopg2.Error as e:
                logger.error(f"Error inserting batch {batch_num}/{total_batches}: {e}")
                self.conn.rollback()
                continue

        cursor.close()
        logger.info(f"Total inserted: {total_inserted} records into {table_name}")
        return total_inserted

    def get_latest_transaction_date(self, table_name: str, date_column: str = 'contract_date') -> Optional[str]:
        """
        Get the most recent transaction date from the table.

        Args:
            table_name: Name of the table
            date_column: Name of the date column

        Returns:
            Latest date as string, or None if table is empty
        """
        try:
            cursor = self.conn.cursor()
            query = f"""
                SELECT {date_column}
                FROM {table_name}
                ORDER BY {date_column} DESC
                LIMIT 1
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

            if result:
                latest_date = result[0]
                logger.info(f"Latest transaction in {table_name}: {latest_date}")
                return latest_date
            else:
                logger.info(f"No transactions found in {table_name}")
                return None

        except psycopg2.Error as e:
            logger.error(f"Error getting latest transaction date from {table_name}: {e}")
            return None

    def get_transaction_count(self, table_name: str) -> int:
        """
        Get total count of transactions in a table.

        Args:
            table_name: Name of the table

        Returns:
            Count of records
        """
        try:
            cursor = self.conn.cursor()
            query = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

            count = result[0] if result else 0
            logger.info(f"Total records in {table_name}: {count}")
            return count

        except psycopg2.Error as e:
            logger.error(f"Error getting count from {table_name}: {e}")
            return 0
