#!/bin/bash
# Run Pertinax GUI tests with xvfb

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting Pertinax GUI test suite..."

# Check if xvfb is available
if ! command -v xvfb-run &> /dev/null; then
    echo -e "${RED}Error: xvfb-run not found. Please install: sudo apt-get install xvfb${NC}"
    exit 1
fi

# Check if robot is available
if ! command -v robot &> /dev/null; then
    echo -e "${RED}Error: robot not found. Please install: pip install -r requirements-test.txt${NC}"
    exit 1
fi

# Activate venv if it exists
if [ -f "$HOME/.venvs/pertinax/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$HOME/.venvs/pertinax/bin/activate"
fi

# Create reports directory
mkdir -p "$PROJECT_ROOT/tests/reports"

# Kill any existing pertinax processes
pkill -f pertinax_gui || true
sleep 1

# Enable accessibility (required for dogtail)
export GTK_MODULES=gail:atk-bridge
export NO_AT_BRIDGE=0
export GSETTINGS_BACKEND=memory

# Enable accessibility in gsettings
gsettings set org.gnome.desktop.interface toolkit-accessibility true 2>/dev/null || true

echo "Running Robot Framework tests with xvfb..."

# Run tests with xvfb and timeout (180 seconds = 3 minutes)
# Use dbus-run-session to provide proper dbus for accessibility
timeout --kill-after=10s 180s dbus-run-session xvfb-run -a robot \
    --outputdir "$PROJECT_ROOT/tests/reports" \
    --loglevel INFO \
    --exitonfailure \
    "$PROJECT_ROOT/tests/gui/" || TEST_RESULT=$?

# Clean up any remaining processes
pkill -f pertinax_gui || true
sleep 1

# Check for timeout (exit code 124)
if [ "${TEST_RESULT:-0}" -eq 124 ]; then
    echo -e "${RED}✗ Tests timed out after 180 seconds${NC}"
    echo "Test report: tests/reports/report.html"
    exit 124
elif [ "${TEST_RESULT:-0}" -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "Test report: tests/reports/report.html"
    exit 0
else
    echo -e "${RED}✗ Tests failed with code ${TEST_RESULT}${NC}"
    echo "Test report: tests/reports/report.html"
    exit ${TEST_RESULT}
fi
