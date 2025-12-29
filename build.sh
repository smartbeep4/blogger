#!/bin/bash
# Build script for Render deployment
# Using Python 3.13 with modern PostgreSQL driver

echo "Checking Python version..."
python --version

echo "Installing dependencies..."
echo "Note: Using psycopg[binary] for Python 3.13+ compatibility"
pip install -r requirements.txt

echo "Build complete!"
