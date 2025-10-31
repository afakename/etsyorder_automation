#!/bin/bash

# SVG to STL Converter - Mac Setup Script
# This script sets up the converter environment on macOS

set -e  # Exit on any error

echo "================================================"
echo "SVG to STL Converter - Setup for Mac"
echo "================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check Python version
echo "🔍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found!"
    echo ""
    echo "Please install Python 3 from:"
    echo "  https://www.python.org/downloads/"
    echo "  or use Homebrew: brew install python3"
    exit 1
fi
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"
echo ""

# Install requirements
echo "📦 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Test installation
echo "🧪 Testing installation..."
python test_installation.py
echo ""

# Make scripts executable
echo "🔓 Making scripts executable..."
chmod +x converter.py
chmod +x test_installation.py
echo "✅ Scripts are executable"
echo ""

echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Test the converter with the example file:"
echo "   python converter.py examples/test_snowflake.svg"
echo ""
echo "2. Convert your own SVG files:"
echo "   python converter.py /path/to/your/design.svg"
echo ""
echo "3. (Optional) Set up Automator for drag-and-drop:"
echo "   See AUTOMATOR_SETUP.md for instructions"
echo ""
echo "To use the converter later, remember to activate the virtual environment:"
echo "   cd $SCRIPT_DIR"
echo "   source venv/bin/activate"
echo ""
echo "Happy converting! 🎉"
echo ""
