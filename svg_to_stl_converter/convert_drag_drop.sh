#!/bin/bash

# SVG to STL Drag & Drop Converter
# Drag SVG files onto this script to convert them

# ⚠️ UPDATE THIS PATH!
CONVERTER_DIR="$HOME/Documents/etsyorder_automation/svg_to_stl_converter"

# Change to converter directory
cd "$CONVERTER_DIR" || {
    osascript -e 'display alert "Error" message "Cannot find converter directory: '"$CONVERTER_DIR"'" as critical'
    exit 1
}

# Activate virtual environment
source venv/bin/activate || {
    osascript -e 'display alert "Error" message "Virtual environment not found. Run setup_mac.sh first." as critical'
    exit 1
}

# Open a terminal window to show progress
clear
echo "=========================================="
echo "   SVG to STL/3MF Converter"
echo "=========================================="
echo ""

# Process each file
SUCCESS_COUNT=0
FAIL_COUNT=0

for file in "$@"; do
    if [[ "$file" == *.svg ]]; then
        echo "Converting: $(basename "$file")"
        if python converter.py "$file"; then
            ((SUCCESS_COUNT++))
            echo "✅ Success!"
        else
            ((FAIL_COUNT++))
            echo "❌ Failed!"
        fi
        echo ""
    else
        echo "⚠️  Skipping (not SVG): $(basename "$file")"
        echo ""
    fi
done

echo "=========================================="
echo "Complete!"
echo "  Successful: $SUCCESS_COUNT"
echo "  Failed: $FAIL_COUNT"
echo "=========================================="
echo ""
echo "Output files are in the same directory as your SVG files."
echo ""
read -p "Press Enter to close..."
