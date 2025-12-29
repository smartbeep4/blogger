#!/bin/bash
# Build script for Render deployment
# This ensures we're using the correct Python version

echo "Checking Python version..."
python --version

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Build complete!"
