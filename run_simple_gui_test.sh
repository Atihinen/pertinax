#!/bin/bash
# Simple test runner for Pertinax GUI tests

# Make sure we're in the project directory
cd "$(dirname "$0")"

# Activate virtual environment
source ~/.venvs/pertinax/bin/activate

# Set environment variables for accessibility
export GTK_MODULES=gail:atk-bridge
export NO_AT_BRIDGE=0
export GSETTINGS_BACKEND=memory

# Enable accessibility (required for dogtail)
gsettings set org.gnome.desktop.interface toolkit-accessibility true 2>/dev/null || true

# Kill any existing pertinax processes
pkill -f pertinax_gui || true
sleep 1

# Create reports directory if it doesn't exist
mkdir -p tests/reports

# Run just the basic operations test for now
echo "Running basic operations tests..."
timeout --kill-after=5s 60s dbus-run-session xvfb-run -a --server-args="-screen 0 1920x1080x24" \
    robot --outputdir tests/reports \
    --loglevel DEBUG \
    --test "Application Launches Successfully" \
    tests/gui/test_basic_operations.robot

EXIT_CODE=$?
if [ $EXIT_CODE -eq 124 ]; then
    echo "Test timed out after 60 seconds"
    pkill -9 -f pertinax_gui || true
elif [ $EXIT_CODE -eq 0 ]; then
    echo "Test passed successfully"
else
    echo "Test failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE
