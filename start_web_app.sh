#!/bin/bash
# Startup script for Etsy Order Automation Web Interface (Mac/Linux)

echo "========================================="
echo "  Etsy Order Automation - Web Interface"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "etsy_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv etsy_env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source etsy_env/bin/activate

# Install/update requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting web application..."
echo "The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

# Start Streamlit
streamlit run web_app.py
