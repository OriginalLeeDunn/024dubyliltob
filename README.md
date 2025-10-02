# Lilybud420 Bot - Dockerized Highrise Bot

A containerized Highrise bot with music, teleportation, and outfit management features.

## Features

- 🎵 Music commands and playlist management
- 📍 Teleportation system with saved points
- 👕 Outfit and item management
- 🎭 Emote commands
- 🐳 Fully containerized with Docker
- 📊 Health monitoring and logging
- 🔄 Auto-restart capabilities

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Highrise bot token and room ID

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd /path/to/lilybud420
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your bot credentials
   ```

3. **Deploy the bot:**
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
HIGHRISE_BOT_TOKEN=your_bot_token_here
HIGHRISE_ROOM_ID=your_room_id_here

# Optional
HIGHRISE_API_KEY=your_api_key_here
```

### Directory Structure

```
lilybud420/
├── lilybud420.py          # Main bot code
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Development orchestration
├── docker-compose.prod.yml # Production orchestration
├── .env.example          # Environment template
├── scripts/
│   ├── deploy.sh         # Deployment script
│   └── monitor.sh        # Monitoring script
├── mp3/                  # Music files directory
├── data/                 # Persistent bot data
└── logs/                 # Application logs
```

## Usage

### Deployment Commands

```bash
# Deploy the bot
./scripts/deploy.sh

# Monitor the bot
./scripts/monitor.sh status    # Show status
./scripts/monitor.sh logs      # Show recent logs
./scripts/monitor.sh follow    # Follow logs in real-time
./scripts/monitor.sh restart   # Restart the bot
./scripts/monitor.sh update    # Update and restart
```

### Docker Commands

```bash
# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f lilybud420-bot

# Stop the bot
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Production Deployment

For production environments with monitoring:

```bash
# Start with monitoring services
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Start with logging services
docker-compose -f docker-compose.prod.yml --profile logging up -d
```

## Bot Commands

The bot responds to various chat commands in Highrise:

### Music Commands
- `/play <song>` - Play a song from the mp3 directory
- `/stop` - Stop current music
- `/list` - List available songs
- `/volume <0-100>` - Set volume level

### Teleportation Commands
- `/tp <point_name>` - Teleport to saved point
- `/savetp <point_name>` - Save current location
- `/listtp` - List saved teleport points
- `/deletetp <point_name>` - Delete teleport point

### Outfit Commands
- `/outfit <category> <item>` - Equip item
- `/remove <category>` - Remove item category
- `/listoutfit` - Show current outfit

### Emote Commands
- `/emote <emote_name>` - Perform emote
- `/listemotes` - List available emotes

## Monitoring and Logs

### Health Checks

The container includes health checks that verify the bot is running properly:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' lilybud420-bot
```

### Log Management

Logs are automatically rotated and stored in the `logs/` directory:

```bash
# View live logs
docker-compose logs -f

# View specific number of log lines
./scripts/monitor.sh logs 100
```

### Resource Monitoring

Monitor resource usage:

```bash
# View resource usage
./scripts/monitor.sh resources

# View detailed stats
docker stats lilybud420-bot
```

## Troubleshooting

### Common Issues

1. **Bot won't start:**
   - Check `.env` file configuration
   - Verify bot token and room ID
   - Check Docker logs: `docker-compose logs`

2. **Permission errors:**
   - Ensure scripts are executable: `chmod +x scripts/*.sh`
   - Check file ownership in mounted volumes

3. **Music not playing:**
   - Verify mp3 files are in the `mp3/` directory
   - Check audio system dependencies in container

4. **Container keeps restarting:**
   - Check logs for error messages
   - Verify network connectivity
   - Ensure Highrise credentials are valid

### Debug Mode

Run the bot in debug mode:

```bash
# Run with debug logging
docker-compose run --rm lilybud420-bot python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from main import main
import asyncio
asyncio.run(main())
"
```

## Development

### Local Development

For development without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

### Testing

Run tests:

```bash
# Run tests in container
docker-compose run --rm lilybud420-bot python -m pytest

# Run tests locally
pytest test_lilybud420.py
```

## Security Considerations

- Bot runs as non-root user in container
- Environment variables are used for sensitive data
- Logs are rotated to prevent disk space issues
- Network isolation through Docker networks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review container logs
- Open an issue on the repository
