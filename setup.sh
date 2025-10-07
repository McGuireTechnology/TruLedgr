#!/bin/bash

echo "🎉 Bonjour! Setting up TruLedgr Development Environment"
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

echo "✅ Prerequisites check passed!"
echo ""

echo "🐍 Setting up Python backend..."
cd api
poetry install
echo "✅ Backend dependencies installed"
echo ""

echo "🌐 Setting up Dashboard frontend..."
cd ../dashboard
npm install
echo "✅ Dashboard frontend dependencies installed"
echo ""

echo "🎨 Setting up landing page..."
cd ../landing
npm install
echo "✅ Landing page dependencies installed"
echo ""

echo "📚 Setting up documentation..."
cd ..
pip install mkdocs-material
echo "✅ MkDocs installed"
echo ""

echo "🎊 Setup complete! You can now run the applications:"
echo ""
echo "Backend API:    cd api && poetry run uvicorn api.main:app --reload"
echo "Dashboard Web App:    cd dashboard && npm run dev"
echo "Landing Page:   cd landing && npm run dev"
echo "iOS/macOS App:  cd apple && swift run"
echo "Android App:    Open android in Android Studio"
echo "Documentation:  mkdocs serve"
echo ""
echo "Visit http://localhost:8000 for the API"
echo "Visit http://localhost:3000 for the dashboard"
echo "Visit http://localhost:5000 for the landing page"
echo "Visit http://localhost:8001 for documentation"