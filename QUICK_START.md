# 🚀 Quick Start Guide

Get your Telegram Expense Tracker Bot running in minutes!

## Prerequisites

- Docker & Docker Compose installed
- Telegram account
- Google account
- Service account JSON from Google Cloud

## 5-Minute Setup

### Step 1: Get Your Credentials (5 min)

**A. Telegram Bot Token**
1. Open Telegram, search `@BotFather`
2. Send `/newbot` and follow prompts
3. Copy your bot token: `123456789:ABC...`

**B. Google Gemini API Key**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

**C. Service Account JSON**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Google Sheets API
3. Create Service Account → Download JSON
4. Share your Google Sheet with service account email (from JSON)

### Step 2: Setup Project (1 min)

```bash
# Clone and enter directory
git clone <repo-url>
cd ai-accounting

# Create credentials directory
mkdir -p credentials

# Copy your service account JSON with EXACT filename
cp ~/Downloads/your-key.json credentials/google_service_account.json

# Create .env from example
cp .env.example .env
```

### Step 3: Configure .env (2 min)

```bash
nano .env
```

Fill in:
```env
TELEGRAM_BOT_TOKEN=123456789:ABC...
GEMINI_API_KEY=AIzaSyABC...
GEMINI_MODEL=gemini-3-flash-preview
GOOGLE_SHEETS_CREDS_FILE=/app/credentials/service_account.json
GOOGLE_SHEET_NAME=Expense_Tracker
```

Save and exit (Ctrl+X, Y, Enter).

### Step 4: Deploy with Docker (2 min)

```bash
# Build the image
docker-compose build

# Start the bot
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f expense-bot
```

You should see:
```
✓ Successfully connected to sheet: Expense_Tracker
✓ Bot initialized successfully
Bot is running!
```

### Step 5: Test It! (1 min)

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Try: `Coffee 5.50 USD`
5. Check your Google Sheet!

## Troubleshooting

**Bot not starting?**
```bash
docker-compose logs expense-bot
```

**File not found error?**
```bash
# Verify filename is EXACT
ls -la credentials/
# Should see: google_service_account.json
```

**Sheet access denied?**
- Open your Google Sheet
- Click Share
- Add service account email (from JSON)
- Give Editor access

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart bot
docker-compose restart

# Stop bot
docker-compose down

# Rebuild after code changes
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Next Steps

- Test with images: Send receipt photo
- Test with voice: Record expense
- Try `/summary` command
- Read [DOCKER.md](DOCKER.md) for advanced usage

## File Structure Checklist

```
ai-accounting/
├── .env                    ✓ Your credentials
├── credentials/
│   └── google_service_account.json  ✓ Service account key
├── docker-compose.yml      ✓ Already configured
└── Dockerfile              ✓ Already configured
```

## Success!

If you see "Bot is running!" in logs and bot responds in Telegram, you're done! 🎉

Need help? Check:
- [README.md](README.md) - Full documentation
- [DOCKER.md](DOCKER.md) - Docker details
- [SETUP.md](SETUP.md) - Manual setup

---

**Total Time: ~10 minutes**
**Difficulty: Easy** ⭐⭐☆☆☆
