#!/bin/bash
# Setup Script for SCM Chatbot
# This script sets up the environment and installs dependencies

echo "========================================="
echo "SCM Chatbot - Setup Script"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python is installed"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ All dependencies installed successfully"
echo ""

# Create necessary directories
echo "Creating required directories..."
mkdir -p logs models/faiss_index

echo "✅ Setup complete!"
echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your API key (if using LangChain):"
echo "   export GROQ_API_KEY='your-api-key-here'"
echo ""
echo "3. Run the chatbot:"
echo "   python main.py --mode cli"
echo "   or"
echo "   python main.py --mode ui"
echo ""
echo "For help: python main.py --help"
echo "========================================="
