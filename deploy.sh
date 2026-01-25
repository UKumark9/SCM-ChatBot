#!/bin/bash
# SCM Chatbot Deployment Script
# This script helps deploy the chatbot to various platforms

set -e

echo "======================================"
echo "SCM Chatbot Deployment Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
print_status "Python 3 is installed"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_status "Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_warning "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_warning "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_warning "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_status "Pip upgraded"

# Install dependencies
print_warning "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
print_status "Dependencies installed"

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    print_warning "GROQ_API_KEY environment variable not set"
    echo ""
    read -p "Enter your Groq API key: " GROQ_KEY
    export GROQ_API_KEY=$GROQ_KEY
    
    # Save to .env file
    echo "GROQ_API_KEY=$GROQ_KEY" > .env
    print_status "API key saved to .env file"
else
    print_status "GROQ_API_KEY is set"
fi

# Check data files
print_warning "Checking data files..."
if [ -d "data/train" ] && [ "$(ls -A data/train)" ]; then
    print_status "Training data found"
else
    print_error "Training data not found in data/train/"
    echo "Please copy the following CSV files to data/train/:"
    echo "  - df_Customers.csv"
    echo "  - df_Orders.csv"
    echo "  - df_OrderItems.csv"
    echo "  - df_Payments.csv"
    echo "  - df_Products.csv"
    exit 1
fi

# Create necessary directories
mkdir -p logs models/faiss_index
print_status "Directories created"

# Run tests (optional)
echo ""
read -p "Run tests before deployment? (y/n): " RUN_TESTS
if [ "$RUN_TESTS" = "y" ]; then
    print_warning "Running tests..."
    python -m pytest tests/test_suite.py -v
    print_status "Tests completed"
fi

# Deployment options
echo ""
echo "======================================"
echo "Deployment Options:"
echo "======================================"
echo "1. Local Development (Gradio UI)"
echo "2. Production Server (with Gunicorn)"
echo "3. Docker Deployment"
echo "4. Cloud Deployment (Instructions)"
echo "5. Exit"
echo ""

read -p "Select deployment option (1-5): " DEPLOY_OPTION

case $DEPLOY_OPTION in
    1)
        print_status "Starting local development server..."
        python main.py --mode ui --port 7860
        ;;
    2)
        print_warning "Installing gunicorn..."
        pip install gunicorn
        print_status "Starting production server..."
        gunicorn -w 4 -b 0.0.0.0:8000 main:app
        ;;
    3)
        print_status "Building Docker image..."
        docker build -t scm-chatbot .
        print_status "Running Docker container..."
        docker run -p 7860:7860 -e GROQ_API_KEY=$GROQ_API_KEY scm-chatbot
        ;;
    4)
        echo ""
        echo "Cloud Deployment Instructions:"
        echo ""
        echo "AWS EC2:"
        echo "  1. Launch EC2 instance (t2.medium or larger)"
        echo "  2. SSH into instance"
        echo "  3. Clone repository"
        echo "  4. Run this script"
        echo "  5. Configure security groups to allow port 7860"
        echo ""
        echo "Google Cloud Run:"
        echo "  gcloud run deploy scm-chatbot \\"
        echo "    --source . \\"
        echo "    --platform managed \\"
        echo "    --region us-central1 \\"
        echo "    --allow-unauthenticated"
        echo ""
        echo "Hugging Face Spaces:"
        echo "  1. Create new Gradio Space"
        echo "  2. Upload files to repository"
        echo "  3. Add GROQ_API_KEY to Secrets"
        echo ""
        ;;
    5)
        print_status "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

print_status "Deployment complete!"
