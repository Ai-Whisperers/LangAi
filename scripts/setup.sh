#!/bin/bash
# Company Researcher - Setup Script
# Sets up development environment

set -e

echo "=================================="
echo "Company Researcher Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

echo -e "\n${YELLOW}Checking Python version...${NC}"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo -e "${GREEN}Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}Python 3.11+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Install development dependencies if they exist
if [ -f "requirements-dev.txt" ]; then
    echo -e "\n${YELLOW}Installing development dependencies...${NC}"
    pip install -r requirements-dev.txt
fi

# Install package in development mode
echo -e "\n${YELLOW}Installing package in development mode...${NC}"
pip install -e .

# Set up environment file
echo -e "\n${YELLOW}Setting up environment file...${NC}"
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${GREEN}.env file created from env.example${NC}"
        echo -e "${YELLOW}Please edit .env and add your API keys${NC}"
    else
        echo -e "${RED}env.example not found${NC}"
    fi
else
    echo ".env file already exists, skipping..."
fi

# Set up pre-commit hooks
echo -e "\n${YELLOW}Setting up pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo -e "${GREEN}Pre-commit hooks installed${NC}"
else
    echo "pre-commit not found, skipping..."
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p data logs cache output

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
python -c "from src.company_researcher import __version__; print(f'Company Researcher version: {__version__}')" 2>/dev/null || echo "Package import check skipped"

echo -e "\n${GREEN}=================================="
echo "Setup complete!"
echo "==================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run 'source venv/bin/activate' to activate the environment"
echo "3. Run 'make test' to verify everything works"
echo ""
