# Etsy Order Automation - Web Interface

A beautiful web-based dashboard for managing your Etsy snowflake ornament orders!

## Quick Start

### Mac/Linux
```bash
./start_web_app.sh
```

### Windows
```
start_web_app.bat
```

The app will automatically open in your browser at `http://localhost:8501`

---

## What You'll See

### 📈 Dashboard Tab
- **Order Statistics**: Overview of all orders
- **Visual Charts**: Breakdown of workflow orders
- **Metrics**: Total orders, needs made, needs updated, already made, preview requests

### 🔔 Preview Requests Tab
- Shows all customers who requested design previews
- Displays customer details, order info, and messages
- Alert if you have pending preview requests

### 🎨 Needs Made Tab
- **MS - Needs Made**: Magic Star orders requiring new designs
- **MS - Needs Updated**: Magic Star orders needing updates
- **RR - Needs Made**: Rainbow Runner orders requiring new designs
- **RR - Needs Updated**: Rainbow Runner orders needing updates
- Interactive tables with all order details

### 📁 Already Made Tab
- Lists all orders with existing designs
- Shows file paths to existing designs
- Ready for 3D printing/production

### 📥 Downloads Tab
- Download full Excel report
- Download CSV files for Adobe Illustrator (MS and RR)
- All files organized by run timestamp

---

## How To Use

### Step 1: Configure Settings
Use the sidebar to:
- Choose **Order Mode**:
  - `Open Orders Only` (Recommended): Only pulls incomplete orders
  - `All Orders (Time-based)`: Pulls all orders in timeframe
- Set **Days to Look Back**: How far back to search for orders

### Step 2: Pull Orders
Click the **"🔄 Pull Orders Now"** button in the sidebar

The app will:
1. Connect to Etsy API
2. Pull all orders matching your criteria
3. Check your design database
4. Categorize orders
5. Generate reports
6. Create Illustrator CSV files

### Step 3: Review Results
Navigate through the tabs to:
- View order statistics
- Check preview requests
- See what needs to be made
- Find existing designs
- Download reports

### Step 4: Download Files
Go to the **Downloads** tab to get:
- Full Excel workbook with all sheets
- CSV files ready for Adobe Illustrator variable data

---

## Features

### 🎯 Smart Detection
- Automatically detects if designs already exist
- Identifies when designs need updates (center or year changes)
- Flags preview requests from customers

### 📊 Visual Analytics
- Beautiful charts showing order breakdowns
- Color-coded metrics
- Interactive data tables

### 🔄 Real-time Updates
- Pull fresh orders anytime
- Instant updates when new orders arrive
- Track order status (New vs. Previously Pulled)

### 📦 Production Ready
- CSV files ready for Adobe Illustrator
- Excel reports organized by workflow
- Slicer batch staging for 3D printing

---

## Understanding the Reports

### Excel Sheets Explained

1. **Preview Requests**: Customers requesting design approval
2. **MS - Needs Made**: New Magic Star designs to create
3. **MS - Needs Updated**: Existing Magic Star designs to modify
4. **RR - Needs Made**: New Rainbow Runner designs to create
5. **RR - Needs Updated**: Existing Rainbow Runner designs to modify
6. **Already Made**: Orders with existing designs ready to go
7. **Peace-Love-Hope Orders**: Special ornament category
8. **Other Orders**: All other product types
9. **All Workflow Orders**: Complete summary of MS/RR orders

### CSV Files for Illustrator

- `illustrator_ms.csv`: Variable data for Magic Star batch
- `illustrator_rr.csv`: Variable data for Rainbow Runner batch

These files can be imported directly into Adobe Illustrator for batch design generation.

---

## Troubleshooting

### App won't start
1. Make sure Python 3.8+ is installed
2. Check that you're in the project directory
3. Try manually: `pip install -r requirements.txt` then `streamlit run web_app.py`

### No data showing
1. Click "Pull Orders Now" first
2. Check your Etsy API credentials in `.env` file
3. Verify your `etsy_tokens.json` is valid

### Error pulling orders
1. Check internet connection
2. Verify Etsy API credentials
3. Check if access token needs refresh (run `python etsy_api_connector.py`)

---

## Command Line Alternative

If you prefer the command line, you can still use:

```bash
# Open orders only (recommended)
python main.py --mode open_only --days 90

# All orders in time period
python main.py --mode time_based --days 30
```

---

## System Requirements

- Python 3.8 or higher
- Internet connection (for Etsy API)
- Modern web browser
- Operating System: Windows, Mac, or Linux

---

## Tips

1. **Run daily**: Pull orders each morning to stay on top of new orders
2. **Check preview requests first**: These customers are waiting for you
3. **Download CSVs**: Use them with your Illustrator variable data workflow
4. **Use Already Made**: These are ready to print - no design work needed!
5. **Bookmark the app**: Keep `http://localhost:8501` handy

---

## Support

For issues or questions:
1. Check this README
2. Review the main project README
3. Check the logs in your output folder

---

**Built with ❄️ using Streamlit**
