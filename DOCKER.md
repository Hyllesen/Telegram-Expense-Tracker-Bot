# Docker Deployment Guide

This guide explains how to deploy the Telegram Expense Tracker Bot using Docker.

## Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 1.29+)
- Your credentials ready (.env file and service account JSON)

## Quick Start

### 1. Prepare Credentials

Create a `credentials` directory and place your service account JSON:

```bash
mkdir -p credentials
cp /path/to/your-service-account.json credentials/google_service_account.json
```

**Important:** The file MUST be named `google_service_account.json` to match the docker-compose.yml mount.

### 2. Update .env File

Make sure your `.env` file has the correct path for Docker:

```env
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3-flash-preview
GOOGLE_SHEETS_CREDS_FILE=/app/credentials/service_account.json
GOOGLE_SHEET_NAME=Expense_Tracker
LOG_LEVEL=INFO
```

**Important Notes:**
- `GOOGLE_SHEETS_CREDS_FILE` uses `/app/credentials/service_account.json` (container path)
- The local file `./credentials/google_service_account.json` is mounted to this path
- The mount is read-only (`:ro`) for security

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f expense-bot
```

## Docker Commands

### Basic Operations

```bash
# Start the bot
docker-compose up -d

# Stop the bot
docker-compose stop

# Restart the bot
docker-compose restart

# Stop and remove containers
docker-compose down

# View logs (follow mode)
docker-compose logs -f expense-bot

# View last 100 lines of logs
docker-compose logs --tail=100 expense-bot

# Check bot status
docker-compose ps
```

### Rebuild After Code Changes

```bash
# Stop, rebuild, and start
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Access Container Shell

```bash
# Open shell in running container
docker-compose exec expense-bot /bin/bash

# Or with docker directly
docker exec -it telegram-expense-bot /bin/bash
```

## Directory Structure

```
ai-accounting/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore          # Files to exclude from image
├── .env                   # Environment variables
├── credentials/           # Service account JSON
│   └── google_service_account.json  # Must be named exactly this
├── logs/                  # Persistent logs
│   └── expense_bot.log
└── src/                   # Source code
```

**Important:** The service account file must be named `google_service_account.json` to match the docker-compose.yml file mount.

## Volume Mounts

The `docker-compose.yml` mounts two volumes:

1. **`./credentials/google_service_account.json:/app/credentials/service_account.json:ro`**
   - Mounts specific service account JSON file (not entire directory)
   - Read-only mount (`:ro`) for security
   - Local: `./credentials/google_service_account.json`
   - Container: `/app/credentials/service_account.json`

2. **`./logs:/app/logs`**
   - Persistent logs directory
   - Read-write for bot to write logs

## Environment Variables

All environment variables from `.env` are automatically loaded into the container via `env_file` directive.

## Health Checks

The container includes a health check that runs every 30 seconds:

```bash
# Check container health
docker inspect telegram-expense-bot | grep -A 10 Health
```

## Resource Limits (Optional)

Uncomment the `deploy` section in `docker-compose.yml` to set resource limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

## Logging

Logs are configured to:
- Rotate after 10MB
- Keep last 3 files
- Write to both container logs and mounted volume

View logs:
```bash
# Container logs
docker-compose logs -f

# Mounted log file
tail -f logs/expense_bot.log
```

## Troubleshooting

### Bot not starting

**Check logs:**
```bash
docker-compose logs expense-bot
```

**Common issues:**
- Missing `.env` file
- Invalid service account path
- Permission denied on credentials directory

### Permission Issues

If you encounter permission issues:
```bash
# Fix credentials permissions
chmod 644 credentials/google_service_account.json
chmod 755 credentials

# Fix logs permissions
chmod 755 logs
```

### Rebuild from scratch

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Container keeps restarting

Check logs for errors:
```bash
docker-compose logs --tail=50 expense-bot
```

Common causes:
- Invalid API keys
- Sheet not accessible
- Network issues

## Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml expense-tracker

# Check services
docker stack services expense-tracker

# View logs
docker service logs expense-tracker_expense-bot
```

### Using Kubernetes

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: expense-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: expense-bot
  template:
    metadata:
      labels:
        app: expense-bot
    spec:
      containers:
      - name: expense-bot
        image: expense-bot:latest
        envFrom:
        - secretRef:
            name: expense-bot-secrets
        volumeMounts:
        - name: credentials
          mountPath: /app/credentials
          readOnly: true
      volumes:
      - name: credentials
        secret:
          secretName: service-account-json
```

### Environment-specific Configurations

Create different `.env` files:

```bash
# Development
.env.dev

# Staging  
.env.staging

# Production
.env.prod
```

Use specific env file:
```bash
docker-compose --env-file .env.prod up -d
```

## Monitoring

### Check container stats

```bash
docker stats telegram-expense-bot
```

### Monitor logs in real-time

```bash
# With docker-compose
docker-compose logs -f --tail=100

# With docker
docker logs -f telegram-expense-bot
```

### Export logs

```bash
docker-compose logs > bot-logs-$(date +%Y%m%d).log
```

## Backup

### Backup logs

```bash
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### Backup credentials

```bash
tar -czf credentials-backup-$(date +%Y%m%d).tar.gz credentials/
```

## Updates

### Update bot code

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Update dependencies

```bash
# Update requirements.txt
# Then rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Security Best Practices

1. **Never commit .env or credentials to Git**
2. **Use read-only mounts for credentials** (`:ro`)
3. **Keep base image updated**: `docker pull python:3.10-slim`
4. **Scan for vulnerabilities**: `docker scan expense-bot`
5. **Use secrets management** in production (Docker Secrets, Vault)

## Multi-Platform Build

Build for multiple architectures:

```bash
# Set up buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t expense-bot:latest \
  --push .
```

## Docker Hub Deployment

```bash
# Tag image
docker tag expense-bot:latest yourusername/expense-bot:latest

# Push to Docker Hub
docker push yourusername/expense-bot:latest

# Pull and run on another machine
docker pull yourusername/expense-bot:latest
docker-compose up -d
```

## Cleanup

```bash
# Remove stopped containers
docker-compose down

# Remove all (including volumes)
docker-compose down -v

# Remove images
docker rmi expense-bot

# Clean up system
docker system prune -a
```

## Performance Tuning

### Optimize image size

The Dockerfile already uses:
- Slim base image
- Multi-stage pattern
- No cache for pip
- Cleanup of apt lists

Current image size: ~200-300MB

### Memory optimization

Monitor memory usage:
```bash
docker stats --no-stream telegram-expense-bot
```

Adjust limits in `docker-compose.yml` if needed.

## Support

For issues:
1. Check logs: `docker-compose logs expense-bot`
2. Verify .env configuration
3. Test credentials outside Docker
4. Check Docker version compatibility

## Example: Complete Deployment

```bash
# 1. Clone repo
git clone <repo-url>
cd ai-accounting

# 2. Setup credentials
mkdir credentials
cp ~/Downloads/service-account.json credentials/

# 3. Create .env
cp .env.example .env
nano .env  # Edit with your keys

# 4. Build and run
docker-compose build
docker-compose up -d

# 5. Check status
docker-compose ps
docker-compose logs -f

# 6. Test bot in Telegram
# Send: /start

# 7. Monitor
docker stats telegram-expense-bot
```

That's it! Your bot is now running in Docker 🎉
