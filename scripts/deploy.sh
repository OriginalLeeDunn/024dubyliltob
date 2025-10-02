#!/bin/bash

# Lilybud420 Bot Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_status "Please copy .env.example to .env and configure your bot credentials"
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$HIGHRISE_BOT_TOKEN" ]; then
    print_error "HIGHRISE_BOT_TOKEN is not set in .env file"
    exit 1
fi

if [ -z "$HIGHRISE_ROOM_ID" ]; then
    print_error "HIGHRISE_ROOM_ID is not set in .env file"
    exit 1
fi

print_status "Starting Lilybud420 bot deployment..."

# Create necessary directories
print_status "Creating directories..."
mkdir -p data logs

# Build the Docker image
print_status "Building Docker image..."
docker build -t lilybud420-bot:latest .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Stop existing container if running
print_status "Stopping existing container..."
docker-compose down 2>/dev/null || true

# Start the bot
print_status "Starting bot container..."
docker-compose up -d

if [ $? -eq 0 ]; then
    print_success "Bot started successfully!"
    print_status "Container status:"
    docker-compose ps
    
    print_status "To view logs, run: docker-compose logs -f"
    print_status "To stop the bot, run: docker-compose down"
else
    print_error "Failed to start bot container"
    exit 1
fi
