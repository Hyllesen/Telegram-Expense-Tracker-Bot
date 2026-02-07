# 🚀 Deployment Checklist

Use this checklist when deploying the Telegram Expense Tracker Bot.

## ✅ Pre-Deployment

### Credentials Setup
- [ ] Telegram Bot Token obtained from @BotFather
- [ ] Google Gemini API Key obtained from AI Studio
- [ ] Google Service Account JSON downloaded
- [ ] Google Sheet created with headers
- [ ] Service account email granted Editor access to sheet

### Local Testing
- [ ] Code tested locally with `pytest`
- [ ] Bot tested with text messages
- [ ] Bot tested with image uploads
- [ ] Bot tested with voice notes
- [ ] All 33 tests passing

## 🐳 Docker Deployment

### Pre-Build
- [ ] Docker and Docker Compose installed
- [ ] `.env` file created from `.env.example`
- [ ] `credentials/` directory created
- [ ] Service account JSON saved as `credentials/google_service_account.json`
- [ ] `.env` updated: `GOOGLE_SHEETS_CREDS_FILE=/app/credentials/service_account.json`

### Build & Deploy
```bash
# Verify Docker is running
docker --version
docker-compose --version

# Build the image
docker-compose build

# Start the bot
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f expense-bot
```

### Post-Deploy Verification
- [ ] Container is running (`docker-compose ps`)
- [ ] No errors in logs (`docker-compose logs`)
- [ ] Bot responds to `/start` in Telegram
- [ ] Test expense logging with text
- [ ] Verify expense appears in Google Sheet
- [ ] Test `/summary` command

## 🖥️ Manual Deployment

### Environment Setup
- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed from `requirements.txt`
- [ ] `.env` file configured
- [ ] Service account JSON accessible

### Run & Verify
```bash
# Activate venv
source venv/bin/activate

# Run tests
pytest tests/ -v

# Start bot
python src/main.py
```

- [ ] Bot starts without errors
- [ ] Logs show successful connection to Google Sheets
- [ ] Bot responds in Telegram

## 🔒 Security Checklist

- [ ] `.env` file NOT committed to Git
- [ ] Service account JSON NOT committed to Git
- [ ] `.gitignore` properly configured
- [ ] API keys kept secret
- [ ] Service account has minimal necessary permissions
- [ ] Docker credentials mounted as read-only

## 📊 Monitoring Setup

### Logs
- [ ] Log directory configured (`./logs`)
- [ ] Log rotation enabled (Docker: 10MB, 3 files)
- [ ] Log level set appropriately (INFO for prod)

### Health Checks
- [ ] Docker health check working (if using Docker)
- [ ] Bot restart policy configured (`unless-stopped`)
- [ ] Resource limits set (optional but recommended)

## 🚨 Troubleshooting

### Common Issues Checklist

#### Bot Not Starting
- [ ] Check `.env` variables are set correctly
- [ ] Verify API keys are valid
- [ ] Check service account JSON path
- [ ] Review logs for error messages

#### Sheet Access Issues
- [ ] Service account email has Editor access
- [ ] Sheet name matches `.env` exactly (case-sensitive)
- [ ] Service account JSON is valid

#### Gemini API Issues
- [ ] API key is valid and not expired
- [ ] API quota not exceeded
- [ ] Model name is correct (`gemini-3-flash-preview`)

#### Docker Issues
- [ ] Docker daemon is running
- [ ] `.env` file exists
- [ ] Credentials directory mounted correctly
- [ ] No port conflicts

## 🔄 Update Procedure

### Code Updates
```bash
# Pull latest code
git pull

# Rebuild (Docker)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or restart (Manual)
# Stop bot, git pull, restart
```

- [ ] Backup current configuration
- [ ] Pull latest changes
- [ ] Run tests
- [ ] Rebuild/restart
- [ ] Verify functionality

## 📝 Production Checklist

### Before Go-Live
- [ ] All tests passing (33/33)
- [ ] Documentation reviewed
- [ ] Credentials secured
- [ ] Backup strategy defined
- [ ] Monitoring configured
- [ ] Error alerting setup (optional)

### Go-Live
- [ ] Deploy bot
- [ ] Verify with test messages
- [ ] Monitor logs for 24 hours
- [ ] Share bot with users

### Post Go-Live
- [ ] Monitor daily for first week
- [ ] Check Google Sheet data accuracy
- [ ] Review error logs
- [ ] Collect user feedback

## 📞 Support Resources

- **Documentation**: README.md, SETUP.md, DOCKER.md
- **Tests**: `pytest tests/ -v`
- **Logs**: `./logs/expense_bot.log` or `docker-compose logs`
- **Issues**: Check GitHub issues (if public repo)

---

**Last Updated**: 2026-02-07
**Version**: 1.0.0
**Status**: Production Ready ✅
