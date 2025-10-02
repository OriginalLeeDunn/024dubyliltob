# Lilybud420 Bot - Deployment Guide

This guide will help you deploy the Lilybud420 Highrise bot using Docker containers.

## Prerequisites

Before deploying, ensure you have:

- ✅ Docker installed (version 20.10+)
- ✅ Docker Compose installed (version 2.0+)
- ✅ Highrise bot token
- ✅ Highrise room ID
- ✅ (Optional) Highrise API key for outfit features

## Step-by-Step Deployment

### 1. Environment Setup

First, configure your bot credentials:

```bash
# Copy the environment template
cp .env.example .env

# Edit the .env file with your credentials
nano .env
```

Your `.env` file should look like:
```env
HIGHRISE_BOT_TOKEN=your_actual_bot_token_here
HIGHRISE_ROOM_ID=your_room_id_here
HIGHRISE_API_KEY=your_api_key_here  # Optional
```

### 2. Quick Deployment

Use the automated deployment script:

```bash
# Make the script executable
chmod +x scripts/deploy.sh

# Deploy the bot
./scripts/deploy.sh
```

### 3. Manual Deployment

If you prefer manual control:

```bash
# Create necessary directories
mkdir -p data logs

# Build the Docker image
docker build -t lilybud420-bot:latest .

# Start the bot
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Using Makefile (Recommended)

For easier management, use the provided Makefile:

```bash
# First-time setup
make setup

# Deploy the bot
make deploy

# Check status
make status

# View logs
make logs

# Follow logs in real-time
make follow
```

## Deployment Options

### Development Deployment

For development and testing:

```bash
# Using docker-compose
docker-compose up -d

# Using Makefile
make start
```

### Production Deployment

For production environments:

```bash
# Basic production deployment
docker-compose -f docker-compose.prod.yml up -d

# With monitoring services
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Using Makefile
make prod-deploy
```

## Verification

After deployment, verify the bot is working:

### 1. Check Container Status

```bash
# Using docker-compose
docker-compose ps

# Using Makefile
make status

# Using monitoring script
./scripts/monitor.sh status
```

Expected output:
```
NAME                COMMAND             SERVICE             STATUS              PORTS
lilybud420-bot      "python main.py"    lilybud420-bot      running (healthy)   8080/tcp
```

### 2. Check Logs

```bash
# View recent logs
docker-compose logs --tail=50 lilybud420-bot

# Follow logs in real-time
docker-compose logs -f lilybud420-bot

# Using scripts
./scripts/monitor.sh logs
./scripts/monitor.sh follow
```

Look for successful startup messages:
```
[INFO] Starting Lilybud420 bot...
[INFO] Room ID: your_room_id
[INFO] API key configured for web API features
[SUCCESS] Bot connected successfully
```

### 3. Test Bot Commands

In your Highrise room, test basic commands:
- `/help` - Should show available commands
- `/listtp` - Should show teleport points
- `/listemotes` - Should show available emotes

## Monitoring and Management

### Container Management

```bash
# Start the bot
make start
# or
docker-compose up -d

# Stop the bot
make stop
# or
docker-compose down

# Restart the bot
make restart
# or
docker-compose restart

# Update and restart
make update
```

### Log Management

```bash
# View logs
make logs                    # Recent logs
make follow                  # Follow in real-time
./scripts/monitor.sh logs 100  # Last 100 lines
```

### Resource Monitoring

```bash
# Check resource usage
./scripts/monitor.sh resources

# Detailed stats
docker stats lilybud420-bot
```

### Health Monitoring

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' lilybud420-bot

# Using monitoring script
./scripts/monitor.sh status
```

## Troubleshooting

### Common Issues

#### 1. Bot Won't Start

**Symptoms:**
- Container exits immediately
- "Bot token invalid" errors

**Solutions:**
```bash
# Check environment variables
cat .env

# Verify token format
echo $HIGHRISE_BOT_TOKEN

# Check logs for specific errors
docker-compose logs lilybud420-bot
```

#### 2. Permission Errors

**Symptoms:**
- "Permission denied" errors
- Scripts won't execute

**Solutions:**
```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix directory permissions
sudo chown -R $USER:$USER data logs
```

#### 3. Container Keeps Restarting

**Symptoms:**
- Container status shows "restarting"
- Frequent restart messages in logs

**Solutions:**
```bash
# Check detailed logs
docker-compose logs --tail=100 lilybud420-bot

# Check resource limits
docker stats lilybud420-bot

# Verify network connectivity
docker-compose exec lilybud420-bot ping google.com
```

#### 4. Music Features Not Working

**Symptoms:**
- Music commands fail
- Audio-related errors

**Solutions:**
```bash
# Check mp3 directory
ls -la mp3/

# Verify audio dependencies in container
docker-compose exec lilybud420-bot python -c "import pydub; print('Audio OK')"
```

### Debug Mode

Run the bot in debug mode for detailed logging:

```bash
# Create debug docker-compose override
cat > docker-compose.debug.yml << EOF
version: '3.8'
services:
  lilybud420-bot:
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=DEBUG
    command: python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from main import main
import asyncio
asyncio.run(main())
"
EOF

# Start in debug mode
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up
```

### Recovery Procedures

#### Complete Reset

If you need to completely reset the deployment:

```bash
# Stop and remove everything
make clean

# Or manually
docker-compose down -v
docker rmi lilybud420-bot:latest
docker system prune -f

# Redeploy
make setup
make deploy
```

#### Data Recovery

Bot data is persisted in the `data/` directory:

```bash
# Backup data
tar -czf lilybud420-backup-$(date +%Y%m%d).tar.gz data/

# Restore data
tar -xzf lilybud420-backup-YYYYMMDD.tar.gz
```

## Maintenance

### Regular Maintenance Tasks

1. **Log Rotation** (automated via Docker)
2. **Container Updates:**
   ```bash
   make update
   ```
3. **Data Backup:**
   ```bash
   cp -r data/ backup/data-$(date +%Y%m%d)/
   ```
4. **Health Checks:**
   ```bash
   ./scripts/monitor.sh status
   ```

### Automated Monitoring

Set up automated monitoring with cron:

```bash
# Add to crontab
crontab -e

# Add these lines:
# Check bot health every 5 minutes
*/5 * * * * cd /path/to/lilybud420 && ./scripts/monitor.sh status > /dev/null || echo "Bot health check failed" | mail -s "Lilybud420 Alert" admin@example.com

# Daily backup
0 2 * * * cd /path/to/lilybud420 && tar -czf backup/data-$(date +\%Y\%m\%d).tar.gz data/
```

## Security Considerations

1. **Environment Variables:** Never commit `.env` files to version control
2. **Container Security:** Bot runs as non-root user
3. **Network Security:** Use Docker networks for isolation
4. **Log Security:** Logs are rotated and size-limited
5. **File Permissions:** Ensure proper ownership of data directories

## Performance Optimization

### Resource Limits

For production, set resource limits in `docker-compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

### Storage Optimization

```bash
# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete

# Clean up Docker images
docker image prune -f
```

## Support

If you encounter issues:

1. Check this deployment guide
2. Review container logs: `make logs`
3. Check the main README.md for bot-specific help
4. Verify your Highrise credentials
5. Test with minimal configuration first

For additional support, ensure you have:
- Container logs
- Environment configuration (without sensitive data)
- Docker and system information
- Steps to reproduce the issue
