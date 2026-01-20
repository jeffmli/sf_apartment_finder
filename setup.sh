#!/bin/bash
# Setup script for SF Apartment Finder

set -e  # Exit on error

echo "🏠 SF Apartment Finder - Setup Script"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✅ Virtual environment recreated"
    fi
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install requirements
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Packages installed"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p output logs
echo "✅ Directories created"
echo ""

# Setup .env file
echo "Setting up environment variables..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists"
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit .env file with your credentials!"
    echo ""
    echo "Required settings:"
    echo "  1. SENDER_EMAIL - Your Gmail address"
    echo "  2. SENDER_PASSWORD - Your Gmail app-specific password"
    echo "  3. RECIPIENT_EMAIL - Where to send apartment listings"
    echo ""
    echo "To get Gmail app password:"
    echo "  1. Go to https://myaccount.google.com/apppasswords"
    echo "  2. Generate password for 'Mail'"
    echo "  3. Copy the 16-character password"
    echo ""
fi

# Review configuration
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your email credentials:"
echo "   nano .env"
echo ""
echo "2. Edit config.yaml with your search criteria:"
echo "   nano config.yaml"
echo ""
echo "3. Test the scraper:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "4. Set up cron job for daily runs:"
echo "   See cron.example for examples"
echo "   crontab -e"
echo ""
echo "For detailed instructions, see SETUP.md"
echo ""
echo "Happy apartment hunting! 🏠"
