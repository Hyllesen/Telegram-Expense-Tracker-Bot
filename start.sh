#!/bin/bash
# Quick start script for Telegram Expense Tracker Bot

set -e

echo "🤖 Telegram Expense Tracker Bot - Quick Start"
echo "=============================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your credentials:"
    echo "   1. TELEGRAM_BOT_TOKEN (from @BotFather)"
    echo "   2. GEMINI_API_KEY (from Google AI Studio)"
    echo "   3. GOOGLE_SHEETS_CREDS_FILE (path to service account JSON)"
    echo "   4. GOOGLE_SHEET_NAME (your Google Sheet name)"
    echo ""
    echo "After editing .env, run this script again."
    exit 0
fi

echo "✓ .env file found"
echo ""

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -q --tb=short
echo "✓ All tests passed!"
echo ""

# Start the bot
echo "🚀 Starting bot..."
echo "=============================================="
python src/main.py
