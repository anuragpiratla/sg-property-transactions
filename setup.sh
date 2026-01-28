#!/bin/bash
# Setup script for Singapore Property Transactions

echo "=================================================="
echo "Singapore Property Transactions Setup"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
echo ""
if [ -f .env ]; then
    echo ".env file already exists"
else
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Note: Please edit .env file and add your credentials:"
    echo "   - DATABASE_URL"
    echo "   - URA_ACCESS_KEY"
fi

echo ""
echo "=================================================="
echo "Setup Complete"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Create PostgreSQL database and run schema.sql"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run: python main.py"
echo ""
echo "For help: python main.py --help"
echo ""
