# Telegram Expense Tracker Bot

A Telegram bot that tracks expenses using Google Gemini's multimodal AI capabilities (text, images, voice) and logs them to Google Sheets.

## Features

- 🤖 **Multimodal Input Support**: Handle text messages, receipt images, and voice notes
- 🧠 **AI-Powered Extraction**: Uses Google Gemini to extract structured expense data
- 📊 **Google Sheets Integration**: Automatically logs expenses to Google Sheets
- 👥 **Multi-User Tracking**: Intelligently extracts "Paid By" information
- 💬 **Interactive Commands**: `/start`, `/help`, `/summary`

## Data Schema

The bot extracts and logs expenses in the following format:

```json
{
  "date": "YYYY-MM-DD",
  "item": "string",
  "amount": float,
  "currency": "string",
  "paid_by": "string"
}
```

## Prerequisites

1. **Python 3.9+**
2. **Telegram Bot Token** - Get from [@BotFather](https://t.me/botfather)
3. **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
4. **Google Service Account** - For Sheets API access
5. **Google Sheet** - Pre-created sheet with columns: Date | Item | Amount | Currency | Paid By

## Quick Start

### Option 1: Quick Start (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ai-accounting

# Run quick start script
chmod +x start.sh
./start.sh

# Edit .env with your credentials
nano .env

# Run start.sh again to launch bot
./start.sh
```

### Option 2: Docker Deployment

```bash
# 1. Setup credentials
mkdir -p credentials
cp /path/to/your-service-account.json credentials/google_service_account.json

# 2. Create and edit .env
cp .env.example .env
nano .env
# Set: GOOGLE_SHEETS_CREDS_FILE=/app/credentials/service_account.json

# 3. Build and run with Docker Compose
docker-compose build
docker-compose up -d

# 4. View logs
docker-compose logs -f
```

**Important for Docker:** 
- Local file: `./credentials/google_service_account.json`
- Container path: `/app/credentials/service_account.json` (set in .env)
- The file is mounted as read-only for security

See **[DOCKER.md](DOCKER.md)** for complete Docker deployment guide.

### Option 3: Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3-flash-preview
GOOGLE_SHEETS_CREDS_FILE=path/to/service-account.json
GOOGLE_SHEET_NAME=Expense_Tracker
```

#### 5. Set Up Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create a Service Account
5. Download JSON credentials
6. Share your Google Sheet with the service account email (found in JSON)
7. Update `GOOGLE_SHEETS_CREDS_FILE` path in `.env`

#### 6. Create Google Sheet

Create a new Google Sheet with the following columns:
```
Date | Item | Amount | Currency | Paid By
```

Update `GOOGLE_SHEET_NAME` in `.env` with your sheet name.

#### 7. Run the Bot

```bash
python src/main.py
```

## Usage

### Text Messages
Simply send a message describing your expense:
```
Coffee at Starbucks 5.50 USD
```

### Receipt Images
Send a photo of your receipt with optional caption:
```
Paid by John
```

### Voice Notes
Record a voice message describing the expense:
```
"Stefan paid for bananas 100 pesos"
```

### Commands

- `/start` - Welcome message and bot introduction
- `/help` - Usage instructions and examples
- `/summary` - View recent expenses (last 10 entries)

## "Paid By" Logic

The bot intelligently extracts who paid for the expense:
- If text contains "Paid by [Name]" or "Bought by [Name]", extracts the name
- Otherwise defaults to "Me"
- Works with images, text, and voice notes

## Testing

The project includes comprehensive unit and integration tests.

### Run All Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

### Run Only Unit Tests

```bash
pytest tests/ -v -m unit
```

### Run Only Integration Tests

```bash
pytest tests/integration_test.py -v
```

### Test Results

✅ **27 Unit Tests** - All passing
- Gemini Handler: 7 tests
- Sheets Handler: 9 tests  
- Bot Handlers: 9 tests
- Coverage: Text, images, voice, error handling

✅ **6 Integration Tests** - All passing
- End-to-end flows
- Multi-modal processing
- "Paid By" extraction logic

### Manual Testing with Test Assets

The `test-assets/` folder contains real files for manual testing:

```bash
# Test with sample images
test-assets/TinePaidForThis353dot50PHP.jpeg
test-assets/TinePaidForThis974PHP.jpeg

# Test with sample voice notes
test-assets/StefanPaidForBananas100Peso.ogg
test-assets/TineBoughtFishFor100Peso.ogg

# Test with text messages
test-assets/test_messages.txt
```

## Project Structure

```
ai-accounting/
├── src/
│   ├── main.py              # Application entry point
│   ├── bot.py               # Telegram bot handlers
│   ├── gemini_handler.py    # Gemini AI integration
│   ├── sheets_handler.py    # Google Sheets integration
│   ├── config.py            # Configuration management
│   └── constants.py         # System prompts and messages
├── tests/
│   ├── test_gemini_handler.py
│   ├── test_sheets_handler.py
│   ├── test_bot.py
│   └── integration_test.py
├── test-assets/             # Sample test data
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Troubleshooting

### Bot not responding
- Check `TELEGRAM_BOT_TOKEN` is correct
- Verify bot is running without errors
- Check logs in `logs/` directory

### Gemini API errors
- Verify `GEMINI_API_KEY` is valid
- Check API quota limits
- Ensure model name is correct

### Google Sheets errors
- Verify service account has edit access to sheet
- Check `GOOGLE_SHEETS_CREDS_FILE` path is correct
- Ensure sheet name matches `GOOGLE_SHEET_NAME`

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
