#!/bin/bash

# Lilybud420 Bot Monitoring Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to show container status
show_status() {
    print_status "Container Status:"
    docker-compose ps
    echo ""
    
    print_status "Container Health:"
    docker inspect --format='{{.State.Health.Status}}' lilybud420-bot 2>/dev/null || echo "No health check configured"
    echo ""
}

# Function to show logs
show_logs() {
    local lines=${1:-50}
    print_status "Recent logs (last $lines lines):"
    docker-compose logs --tail=$lines lilybud420-bot
}

# Function to show resource usage
show_resources() {
    print_status "Resource Usage:"
    docker stats --no-stream lilybud420-bot 2>/dev/null || print_warning "Container not running"
    echo ""
}

# Function to restart the bot
restart_bot() {
    print_status "Restarting bot..."
    docker-compose restart lilybud420-bot
    sleep 5
    show_status
}

# Function to update and restart
update_bot() {
    print_status "Updating bot..."
    docker-compose down
    docker build -t lilybud420-bot:latest .
    docker-compose up -d
    print_success "Bot updated and restarted"
}

# Main menu
case "${1:-status}" in
    "status"|"s")
        show_status
        ;;
    "logs"|"l")
        show_logs ${2:-50}
        ;;
    "follow"|"f")
        print_status "Following logs (Ctrl+C to exit):"
        docker-compose logs -f lilybud420-bot
        ;;
    "resources"|"r")
        show_resources
        ;;
    "restart")
        restart_bot
        ;;
    "update"|"u")
        update_bot
        ;;
    "stop")
        print_status "Stopping bot..."
        docker-compose down
        print_success "Bot stopped"
        ;;
    "start")
        print_status "Starting bot..."
        docker-compose up -d
        sleep 3
        show_status
        ;;
    "help"|"h"|*)
        echo "Lilybud420 Bot Monitor"
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  status, s          Show container status (default)"
        echo "  logs, l [lines]    Show recent logs (default: 50 lines)"
        echo "  follow, f          Follow logs in real-time"
        echo "  resources, r       Show resource usage"
        echo "  restart            Restart the bot"
        echo "  update, u          Update and restart the bot"
        echo "  start              Start the bot"
        echo "  stop               Stop the bot"
        echo "  help, h            Show this help message"
        ;;
esac
