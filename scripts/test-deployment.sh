#!/bin/bash

# Lilybud420 Bot Deployment Test Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        print_success "$test_name"
        ((TESTS_PASSED++))
    else
        print_error "$test_name"
        ((TESTS_FAILED++))
    fi
}

print_status "Starting Lilybud420 Bot Deployment Tests..."
echo ""

# Test 1: Check Docker installation
run_test "Docker installation" "docker --version"

# Test 2: Check Docker Compose installation
run_test "Docker Compose installation" "docker-compose --version"

# Test 3: Check if .env.example exists
run_test ".env.example file exists" "test -f .env.example"

# Test 4: Check if Dockerfile exists
run_test "Dockerfile exists" "test -f Dockerfile"

# Test 5: Check if docker-compose.yml exists
run_test "docker-compose.yml exists" "test -f docker-compose.yml"

# Test 6: Check if requirements.txt exists
run_test "requirements.txt exists" "test -f requirements.txt"

# Test 7: Check if main bot file exists
run_test "lilybud420.py exists" "test -f lilybud420.py"

# Test 8: Check if main.py exists
run_test "main.py exists" "test -f main.py"

# Test 9: Check if scripts directory exists
run_test "scripts directory exists" "test -d scripts"

# Test 10: Check if deploy script exists and is executable
run_test "deploy.sh exists and executable" "test -x scripts/deploy.sh"

# Test 11: Check if monitor script exists and is executable
run_test "monitor.sh exists and executable" "test -x scripts/monitor.sh"

# Test 12: Check if mp3 directory exists
run_test "mp3 directory exists" "test -d mp3"

# Test 13: Test Docker build
print_status "Testing Docker build (this may take a moment)..."
if docker build -t lilybud420-bot:test . >/dev/null 2>&1; then
    print_success "Docker build successful"
    ((TESTS_PASSED++))
else
    print_error "Docker build failed"
    ((TESTS_FAILED++))
fi

# Test 14: Validate docker-compose syntax
run_test "docker-compose.yml syntax validation" "docker-compose config"

# Test 15: Check if .env file exists (warning if not)
if [ -f .env ]; then
    print_success ".env file exists"
    ((TESTS_PASSED++))
    
    # Test 16: Check if required environment variables are set
    if grep -q "HIGHRISE_BOT_TOKEN=" .env && grep -q "HIGHRISE_ROOM_ID=" .env; then
        print_success "Required environment variables configured"
        ((TESTS_PASSED++))
    else
        print_error "Required environment variables not configured in .env"
        ((TESTS_FAILED++))
    fi
else
    print_warning ".env file not found - copy .env.example to .env and configure"
    print_warning "This is required for deployment but not for testing"
fi

# Test 17: Check Python syntax of main files
run_test "Python syntax check - main.py" "python3 -m py_compile main.py"
run_test "Python syntax check - lilybud420.py" "python3 -m py_compile lilybud420.py"

# Test 18: Check if data and logs directories exist or can be created
run_test "data directory creation" "mkdir -p data"
run_test "logs directory creation" "mkdir -p logs"

echo ""
print_status "Test Summary:"
echo "  Tests Passed: $TESTS_PASSED"
echo "  Tests Failed: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All tests passed! Your deployment is ready."
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.example to .env and configure your bot credentials"
    echo "2. Run: ./scripts/deploy.sh"
    echo "3. Monitor with: ./scripts/monitor.sh status"
    exit 0
else
    print_error "Some tests failed. Please fix the issues before deploying."
    exit 1
fi
