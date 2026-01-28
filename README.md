# Singapore Property Transactions

Python tool to fetch and store property transaction data for HDB, condominiums, and landed properties in Singapore.

## Overview

This project retrieves property transaction data from official Singapore government APIs and stores the raw responses in a PostgreSQL database:

- **HDB Transactions**: Fetched via data.gov.sg API
- **Condo Transactions**: Retrieved from URA (Urban Redevelopment Authority) API
- **Landed Property Transactions**: Retrieved from URA API

Data is stored in PostgreSQL as received from the APIs.

## Features

- Fetches private property transactions from URA API
- Separate storage for condo and landed property transactions
- Built-in retry logic for API resilience
- Duplicate prevention using unique constraints
- Batch processing for large datasets
- Configurable via environment variables
- Optional rental transaction data

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database (local or hosted)
- URA API access key

## URA API Access

To obtain a URA API access key:

1. Visit [URA API Registration](https://www.ura.gov.sg/maps/api/)
2. Register for an account
3. Request an access key for "Property Information"
4. You'll receive your AccessKey via email

Note: The URA API provides data for the last 4 quarters. For historical data beyond that, run this tool quarterly.

## Setup

### Quick Setup

Run the setup script:

```bash
./setup.sh
```

The script creates a Python virtual environment, installs dependencies, and creates a `.env` file from the template.

### Manual Setup

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` and add your credentials:
```
DATABASE_URL=postgresql://user:password@localhost:5432/property_transactions
URA_ACCESS_KEY=your_ura_api_access_key
```

### Database Setup

1. Create a PostgreSQL database:
```bash
createdb property_transactions
```

2. Run the schema:
```bash
psql property_transactions < schema.sql
```

This creates the `condo_transactions`, `landed_transactions`, and `rental_transactions` tables with indexes.

## Usage

### Basic Usage

Fetch and store all available property transactions:

```bash
python main.py
```

### Include Rental Data

To also fetch rental transactions:

```bash
python main.py --include-rentals
```

### View Statistics Only

To see database statistics without fetching new data:

```bash
python main.py --stats-only
```

### Help

```bash
python main.py --help
```

## Project Structure

```
sg-property-transactions/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── schema.sql               # Database schema
├── setup.sh                 # Setup script
├── config.py                # Configuration management
├── main.py                  # Main script
├── scrapers/
│   ├── __init__.py
│   └── ura_scraper.py       # URA API client
└── db/
    ├── __init__.py
    └── db_client.py         # PostgreSQL client
```

## Data Schema

### Condo Transactions

Each condo transaction record includes:
- `project_name`: Name of the condo project
- `street`: Street address
- `x_coordinate`, `y_coordinate`: Location coordinates
- `area`: Floor area
- `floor_range`: Floor level range
- `no_of_units`: Number of units transacted
- `contract_date`: Date of transaction
- `type_of_sale`: Sale type (New Sale, Resale, etc.)
- `price`: Transaction price
- `property_type`: Type of property (Apartment, Condominium, etc.)
- `district`: Planning district
- `type_of_area`: Area measurement type
- `tenure`: Freehold/Leasehold
- `market_segment`: Market segment (RCR, CCR, OCR)
- `batch`: API batch number
- `scraped_at`: Timestamp when fetched

### Landed Transactions

Similar schema to condo transactions, for landed properties (Detached Houses, Semi-Detached Houses, Terrace Houses).

## Data Coverage

- **URA API**: Provides data for the last 4 quarters (approximately 1 year)
- **Update Frequency**: URA updates their data quarterly
- **Recommended Schedule**: Run this tool monthly or quarterly to maintain historical data

## Scheduling Regular Updates

To keep data up-to-date, schedule the tool to run automatically:

### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line to run on the 1st of every month at 2 AM
0 2 1 * * /path/to/pp/venv/bin/python /path/to/pp/main.py
```

### Using GitHub Actions

Create `.github/workflows/fetch.yml`:

```yaml
name: Property Data Fetch

on:
  schedule:
    - cron: '0 2 1 * *'  # Monthly on the 1st at 2 AM UTC
  workflow_dispatch:  # Allow manual triggers

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          URA_ACCESS_KEY: ${{ secrets.URA_ACCESS_KEY }}
```

## Troubleshooting

### Configuration Errors

"Missing required environment variables":
- Check that `.env` file exists
- Verify all required variables are set
- Ensure no extra spaces around the `=` sign

### API Errors

URA API errors:
- Verify URA_ACCESS_KEY is correct
- Check rate limits haven't been exceeded
- Ensure URA API subscription is active

### Database Errors

PostgreSQL errors:
- Verify DATABASE_URL is correct
- Check that `schema.sql` has been run to create tables
- Ensure database user has the necessary permissions

## Data Analysis

Query data in PostgreSQL:

```sql
-- Average condo price by district (last quarter)
SELECT
    district,
    COUNT(*) as num_transactions,
    AVG(CAST(price AS NUMERIC)) as avg_price
FROM condo_transactions
WHERE contract_date >= DATE_TRUNC('quarter', CURRENT_DATE)
GROUP BY district
ORDER BY avg_price DESC;

-- Landed property transactions by type
SELECT
    property_type,
    COUNT(*) as count,
    MIN(CAST(price AS NUMERIC)) as min_price,
    MAX(CAST(price AS NUMERIC)) as max_price,
    AVG(CAST(price AS NUMERIC)) as avg_price
FROM landed_transactions
GROUP BY property_type
ORDER BY count DESC;
```

## License

MIT License

## Disclaimer

This tool is for educational and research purposes. Users must:
- Respect URA's API rate limits
- Review and comply with URA's terms of service
- Verify data accuracy from official sources
- Obtain proper licensing before commercial use