"""
URA (Urban Redevelopment Authority) API client.

Fetches private property (condo and landed) transaction data from URA API.
"""
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class URAScraper:
    """Client for URA private property transactions API."""

    def __init__(self, access_key: str, base_url: str):
        """
        Initialize URA API client.

        Args:
            access_key: URA API access key
            base_url: Base URL for URA API
        """
        self.access_key = access_key
        self.base_url = base_url
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """
        Generate headers for URA API request.

        Returns:
            Dictionary of headers including AccessKey and User-Agent
        """
        return {
            'AccessKey': self.access_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_request(self, params: Dict[str, str]) -> Optional[Dict]:
        """
        Make request to URA API with retry logic.

        Args:
            params: Query parameters for the request

        Returns:
            JSON response as dictionary, or None if request fails
        """
        try:
            response = self.session.get(
                self.base_url,
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_private_residential_transactions(self, batch: int = 1) -> List[Dict]:
        """
        Fetch private residential property transactions.

        The URA API returns data in batches:
        - Batch 1: Latest quarter
        - Batch 2: Previous quarter
        - Batch 3: 2 quarters ago
        - Batch 4: 3 quarters ago

        Args:
            batch: Batch number (1-4)

        Returns:
            List of transaction records
        """
        params = {
            'service': 'PMI_Resi_Transaction',
            'batch': str(batch)
        }

        logger.info(f"Fetching private residential transactions (batch {batch})...")

        try:
            data = self._make_request(params)

            if not data or 'Result' not in data:
                logger.warning(f"No data returned for batch {batch}")
                return []

            transactions = []
            result = data.get('Result', [])

            for project in result:
                project_name = project.get('project', '')
                street = project.get('street', '')
                x_coord = project.get('x', '')
                y_coord = project.get('y', '')

                for transaction in project.get('transaction', []):
                    record = {
                        'project_name': project_name,
                        'street': street,
                        'x_coordinate': x_coord,
                        'y_coordinate': y_coord,
                        'area': transaction.get('area', ''),
                        'floor_range': transaction.get('floorRange', ''),
                        'no_of_units': transaction.get('noOfUnits', ''),
                        'contract_date': transaction.get('contractDate', ''),
                        'type_of_sale': transaction.get('typeOfSale', ''),
                        'price': transaction.get('price', ''),
                        'property_type': transaction.get('propertyType', ''),
                        'district': transaction.get('district', ''),
                        'type_of_area': transaction.get('typeOfArea', ''),
                        'tenure': transaction.get('tenure', ''),
                        'market_segment': transaction.get('marketSegment', ''),
                        'batch': batch,
                        'scraped_at': datetime.now().isoformat()
                    }
                    transactions.append(record)

            logger.info(f"Fetched {len(transactions)} transactions from batch {batch}")
            return transactions

        except Exception as e:
            logger.error(f"Error fetching batch {batch}: {e}")
            return []

    def get_all_available_transactions(self) -> Dict[str, List[Dict]]:
        """
        Fetch all available private property transactions.

        Returns:
            Dictionary with 'condo' and 'landed' keys containing transaction lists
        """
        all_transactions = []

        # Fetch data from all 4 batches
        for batch in range(1, 5):
            transactions = self.get_private_residential_transactions(batch)
            all_transactions.extend(transactions)
            time.sleep(1)

        # Separate by property type
        condo_transactions = []
        landed_transactions = []

        for txn in all_transactions:
            property_type = txn.get('property_type', '').upper()

            # Landed types: Detached House, Semi-Detached House, Terrace House
            if any(landed_type in property_type for landed_type in
                   ['DETACHED', 'TERRACE', 'BUNGALOW']):
                landed_transactions.append(txn)
            else:
                condo_transactions.append(txn)

        logger.info(f"Total transactions: {len(all_transactions)}")
        logger.info(f"Condo transactions: {len(condo_transactions)}")
        logger.info(f"Landed transactions: {len(landed_transactions)}")

        return {
            'condo': condo_transactions,
            'landed': landed_transactions
        }

    def get_rental_transactions(self, batch: int = 1) -> List[Dict]:
        """
        Fetch private property rental transactions.

        Args:
            batch: Batch number

        Returns:
            List of rental transaction records
        """
        params = {
            'service': 'PMI_Resi_Rental',
            'batch': str(batch)
        }

        logger.info(f"Fetching rental transactions (batch {batch})...")

        try:
            data = self._make_request(params)

            if not data or 'Result' not in data:
                logger.warning(f"No rental data returned for batch {batch}")
                return []

            rentals = []
            result = data.get('Result', [])

            for project in result:
                project_name = project.get('project', '')
                street = project.get('street', '')
                x_coord = project.get('x', '')
                y_coord = project.get('y', '')

                for rental in project.get('rental', []):
                    record = {
                        'project_name': project_name,
                        'street': street,
                        'x_coordinate': x_coord,
                        'y_coordinate': y_coord,
                        'area_sqm': rental.get('areaSqm', ''),
                        'rent': rental.get('rent', ''),
                        'lease_date': rental.get('leaseDate', ''),
                        'property_type': rental.get('propertyType', ''),
                        'district': rental.get('district', ''),
                        'batch': batch,
                        'scraped_at': datetime.now().isoformat()
                    }
                    rentals.append(record)

            logger.info(f"Fetched {len(rentals)} rentals from batch {batch}")
            return rentals

        except Exception as e:
            logger.error(f"Error fetching rental batch {batch}: {e}")
            return []
