# Setup Guide - Telegram Expense Tracker Bot

This guide walks you through setting up the Telegram Expense Tracker Bot from scratch.

## Prerequisites

- Python 3.9 or higher
- A Telegram account
- A Google account
- Basic command line knowledge

## Step 1: Get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Save this token - you'll need it later

## Step 2: Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the API key
5. Save this key - you'll need it later

## Step 3: Set Up Google Service Account

### 3.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Note your project name

### 3.2 Enable Google Sheets API

1. In your project, go to **APIs & Services** > **Library**
2. Search for "Google Sheets API"
3. Click **Enable**

### 3.3 Create Service Account

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **Service Account**
3. Name it (e.g., "expense-tracker-bot")
4. Click **Create and Continue**
5. Grant role: **Editor** (or Basic > Editor)
6. Click **Done**

### 3.4 Download Credentials

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Choose **JSON** format
5. Download the JSON file
6. Save it securely (e.g., `~/credentials/expense-tracker-service-account.json`)

## Step 4: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it (e.g., "Expense_Tracker")
4. Add header row in first row:
   ```
   Date | Item | Amount | Currency | Paid By
   ```
5. **Important**: Share this sheet with your service account email
   - Click **Share** button
   - Add the service account email (found in the JSON file: `client_email`)
   - Give **Editor** access
   - Click **Send**

## Step 5: Clone and Setup Project

```bash
# Clone repository
cd ~/projects
git clone <your-repo-url>
cd ai-accounting

# Make quick start script executable
chmod +x start.sh

# Run quick start (will create .env)
./start.sh
```

The script will:
- Create virtual environment
- Install dependencies
- Create `.env` file from template
- Prompt you to add credentials

## Step 6: Configure Environment Variables

Edit the `.env` file:

```bash
nano .env
```

Fill in your credentials:

```env
# From Step 1
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# From Step 2
GEMINI_API_KEY=AIzaSyABC...xyz

# Keep default or change if needed
GEMINI_MODEL=gemini-3-flash-preview

# From Step 3.4 (full path to JSON file)
GOOGLE_SHEETS_CREDS_FILE=/Users/yourname/credentials/expense-tracker-service-account.json

# From Step 4 (exact name of your Google Sheet)
GOOGLE_SHEET_NAME=Expense_Tracker

# Optional
LOG_LEVEL=INFO
```

Save and exit (Ctrl+X, then Y, then Enter).

## Step 7: Run Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v
```

You should see all tests passing ✅

## Step 8: Start the Bot

```bash
# If venv is not activated
source venv/bin/activate

# Start the bot
python src/main.py
```

You should see:
```
============================================================
Starting Telegram Expense Tracker Bot
============================================================
Gemini Model: gemini-3-flash-preview
Sheet Name: Expense_Tracker
------------------------------------------------------------
✓ Environment variables validated
✓ Successfully connected to sheet: Expense_Tracker
✓ Bot initialized successfully
============================================================
Bot is running! Press Ctrl+C to stop.
============================================================
```

## Step 9: Test the Bot

1. Open Telegram
2. Search for your bot (the name you gave it)
3. Send `/start`
4. Try these examples:

**Text:**
```
Coffee 5.50 USD
```

**With "Paid By":**
```
Paid by John: Lunch 25 PHP
```

**Image:**
- Send a photo of a receipt
- Add caption: `Paid by Sarah`

**Voice Note:**
- Record: "Stefan paid 100 pesos for bananas"

Check your Google Sheet - expenses should appear! 📊

## Troubleshooting

### Bot not responding

**Check bot token:**
```bash
# In .env, verify TELEGRAM_BOT_TOKEN is correct
```

**Check logs:**
```bash
tail -f logs/expense_bot.log
```

### Gemini API errors

**Verify API key:**
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check if key is valid and not expired

**Check quota:**
- Gemini API has rate limits
- Wait a few minutes and try again

### Google Sheets errors

**Sheet not found:**
- Verify `GOOGLE_SHEET_NAME` exactly matches your sheet name
- Check case sensitivity

**Permission denied:**
- Verify service account email has **Editor** access to sheet
- Check in JSON file for correct email

**Invalid credentials:**
- Verify `GOOGLE_SHEETS_CREDS_FILE` path is correct
- Check JSON file is valid (not corrupted)

### Import errors

**Reinstall dependencies:**
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Production Deployment

### Run as Background Service (Linux/Mac)

Create systemd service file: `/etc/systemd/system/expense-bot.service`

```ini
[Unit]
Description=Telegram Expense Tracker Bot
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/ai-accounting
Environment="PATH=/path/to/ai-accounting/venv/bin"
ExecStart=/path/to/ai-accounting/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable expense-bot
sudo systemctl start expense-bot
sudo systemctl status expense-bot
```

### Run with Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
```

Build and run:
```bash
docker build -t expense-bot .
docker run -d --env-file .env expense-bot
```

## Need Help?

- Check logs: `tail -f logs/expense_bot.log`
- Run tests: `pytest tests/ -v`
- Review README.md for usage examples

Happy expense tracking! 🎉
