-- Database schema for Singapore property transactions
-- Run this with: psql property_transactions < schema.sql

-- Condo transactions table
CREATE TABLE IF NOT EXISTS condo_transactions (
    id BIGSERIAL PRIMARY KEY,
    project_name TEXT,
    street TEXT,
    x_coordinate TEXT,
    y_coordinate TEXT,
    area TEXT,
    floor_range TEXT,
    no_of_units TEXT,
    contract_date TEXT,
    type_of_sale TEXT,
    price TEXT,
    property_type TEXT,
    district TEXT,
    type_of_area TEXT,
    tenure TEXT,
    market_segment TEXT,
    batch INTEGER,
    scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Create a unique constraint to prevent duplicates
    CONSTRAINT unique_condo_transaction UNIQUE (
        project_name, street, contract_date, price, area, floor_range
    )
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_condo_contract_date ON condo_transactions(contract_date);
CREATE INDEX IF NOT EXISTS idx_condo_project_name ON condo_transactions(project_name);
CREATE INDEX IF NOT EXISTS idx_condo_district ON condo_transactions(district);
CREATE INDEX IF NOT EXISTS idx_condo_scraped_at ON condo_transactions(scraped_at);

-- Landed property transactions table
CREATE TABLE IF NOT EXISTS landed_transactions (
    id BIGSERIAL PRIMARY KEY,
    project_name TEXT,
    street TEXT,
    x_coordinate TEXT,
    y_coordinate TEXT,
    area TEXT,
    floor_range TEXT,
    no_of_units TEXT,
    contract_date TEXT,
    type_of_sale TEXT,
    price TEXT,
    property_type TEXT,
    district TEXT,
    type_of_area TEXT,
    tenure TEXT,
    market_segment TEXT,
    batch INTEGER,
    scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Create a unique constraint to prevent duplicates
    CONSTRAINT unique_landed_transaction UNIQUE (
        project_name, street, contract_date, price, area
    )
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_landed_contract_date ON landed_transactions(contract_date);
CREATE INDEX IF NOT EXISTS idx_landed_project_name ON landed_transactions(project_name);
CREATE INDEX IF NOT EXISTS idx_landed_district ON landed_transactions(district);
CREATE INDEX IF NOT EXISTS idx_landed_property_type ON landed_transactions(property_type);
CREATE INDEX IF NOT EXISTS idx_landed_scraped_at ON landed_transactions(scraped_at);

-- Optional: Rental transactions table (if you want to store rental data)
CREATE TABLE IF NOT EXISTS rental_transactions (
    id BIGSERIAL PRIMARY KEY,
    project_name TEXT,
    street TEXT,
    x_coordinate TEXT,
    y_coordinate TEXT,
    area_sqm TEXT,
    rent TEXT,
    lease_date TEXT,
    property_type TEXT,
    district TEXT,
    batch INTEGER,
    scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Create a unique constraint to prevent duplicates
    CONSTRAINT unique_rental_transaction UNIQUE (
        project_name, street, lease_date, rent, area_sqm
    )
);

CREATE INDEX IF NOT EXISTS idx_rental_lease_date ON rental_transactions(lease_date);
CREATE INDEX IF NOT EXISTS idx_rental_project_name ON rental_transactions(project_name);
CREATE INDEX IF NOT EXISTS idx_rental_district ON rental_transactions(district);
