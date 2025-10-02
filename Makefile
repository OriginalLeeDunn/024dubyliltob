# Lilybud420 Bot Makefile

.PHONY: help build start stop restart logs status clean test deploy update

# Default target
help:
	@echo "Lilybud420 Bot - Available Commands:"
	@echo ""
	@echo "  make build     - Build the Docker image"
	@echo "  make start     - Start the bot container"
	@echo "  make stop      - Stop the bot container"
	@echo "  make restart   - Restart the bot container"
	@echo "  make logs      - Show container logs"
	@echo "  make follow    - Follow logs in real-time"
	@echo "  make status    - Show container status"
	@echo "  make clean     - Remove containers and images"
	@echo "  make test      - Run tests"
	@echo "  make deploy    - Deploy the bot (build + start)"
	@echo "  make update    - Update and restart the bot"
	@echo "  make shell     - Open shell in running container"
	@echo ""

# Build the Docker image
build:
	@echo "Building Lilybud420 bot image..."
	docker build -t lilybud420-bot:latest .

# Start the bot
start:
	@echo "Starting Lilybud420 bot..."
	docker-compose up -d
	@make status

# Stop the bot
stop:
	@echo "Stopping Lilybud420 bot..."
	docker-compose down

# Restart the bot
restart:
	@echo "Restarting Lilybud420 bot..."
	docker-compose restart
	@sleep 3
	@make status

# Show logs
logs:
	docker-compose logs --tail=50 lilybud420-bot

# Follow logs
follow:
	docker-compose logs -f lilybud420-bot

# Show status
status:
	@echo "Container Status:"
	@docker-compose ps
	@echo ""
	@echo "Health Status:"
	@docker inspect --format='{{.State.Health.Status}}' lilybud420-bot 2>/dev/null || echo "Container not running"

# Clean up
clean:
	@echo "Cleaning up containers and images..."
	docker-compose down -v
	docker rmi lilybud420-bot:latest 2>/dev/null || true
	docker system prune -f

# Run tests
test:
	@echo "Running tests..."
	docker-compose run --rm lilybud420-bot python -m pytest test_lilybud420.py -v

# Deploy (build and start)
deploy: build start
	@echo "Deployment complete!"
	@echo "Run 'make logs' to view logs or 'make status' to check status"

# Update and restart
update:
	@echo "Updating Lilybud420 bot..."
	@make stop
	@make build
	@make start
	@echo "Update complete!"

# Open shell in running container
shell:
	docker-compose exec lilybud420-bot /bin/bash

# Production deployment
prod-deploy:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d --build

# Production with monitoring
prod-monitor:
	@echo "Deploying to production with monitoring..."
	docker-compose -f docker-compose.prod.yml --profile monitoring up -d --build

# Check environment
check-env:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found!"; \
		echo "Please copy .env.example to .env and configure your settings"; \
		exit 1; \
	fi
	@echo "Environment configuration found ✓"

# Setup (first time setup)
setup: check-env
	@echo "Setting up Lilybud420 bot..."
	@mkdir -p data logs
	@chmod +x scripts/*.sh
	@echo "Setup complete! Run 'make deploy' to start the bot"
