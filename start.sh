
#!/bin/bash

# ArkTS Knowledge Graph - Startup Script

echo "=================================="
echo "  ArkTS Knowledge Graph"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &amp;&gt; /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &amp;&gt; /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

echo "📦 Installing dependencies..."
echo ""

# Install backend dependencies
cd backend
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
echo "Installing frontend dependencies..."
npm install

# Build frontend
echo "Building frontend..."
npm run build

# Go back to backend directory and start server
cd ../backend
echo ""
echo "🚀 Starting server on http://localhost:8000"
echo ""
echo "Open the URL in your browser to use the application."
echo ""

python main.py
