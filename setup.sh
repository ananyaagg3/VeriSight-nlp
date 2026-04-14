#!/bin/bash

# Setup script for Explainable Misinformation Detection System

echo "🚀 Setting up Explainable Misinformation Detection System..."

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check Node version
echo "Checking Node version..."
node_version=$(node --version)
echo "Node version: $node_version"

# Create virtual environment
echo "Creating Python virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy multilingual model..."
python -m spacy download xx_ent_wiki_sm

# Go back to root
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install

# Go back to root
cd ..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and MongoDB URI"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Start backend: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Visit http://localhost:5173"
