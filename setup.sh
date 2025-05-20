#!/bin/bash

# RMU E-Voting System Setup Script

echo "Setting up RMU E-Voting System..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

echo "Setup complete! You can now run the application with 'python run.py'"
