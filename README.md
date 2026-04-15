# Etsy Order Automation

Automated order processing and design management for personalized Etsy snowflake ornaments.

## Overview

This automation system helps manage your Etsy shop by:
- Pulling orders from Etsy API
- Categorizing products (MS, RR, Peace/Love/Hope, Other)
- Checking if designs already exist in your database
- Detecting customer preview requests
- Generating Excel reports and CSV files for Adobe Illustrator
- Staging files for 3D printing

---

## 🌐 Web Interface (NEW!)

The easiest way to use this tool is through the **web dashboard**.

### Quick Start

**Mac/Linux:**
```bash
./start_web_app.sh
```

**Windows:**
```
start_web_app.bat
```

The web app will open at `http://localhost:8501`

### Features
- 📊 Visual dashboard with charts and statistics
- 🔔 Preview request alerts
- 📥 One-click report downloads
- 🎨 Interactive order tables
- 🔄 Real-time order pulling

📖 **[Read the Web App Guide](WEB_APP_README.md)** for detailed instructions.

---

## 💻 Command Line Interface

For automation scripts or advanced users:

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/afakename/etsyorder_automation.git
cd etsyorder_automation
```

2. **Set up virtual environment**
```bash
python3 -m venv etsy_env
source etsy_env/bin/activate  # Mac/Linux
# or
etsy_env\Scripts\activate.bat  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Etsy API**

Create a `.env` file:
```
ETSY_CLIENT_ID=your_client_id
ETSY_CLIENT_SECRET=your_client_secret
```

5. **Authenticate with Etsy**
```bash
python etsy_api_connector.py
```

### Usage

**Pull open orders (recommended):**
```bash
python main.py --mode open_only --days 90
```

**Pull all orders in time period:**
```bash
python main.py --mode time_based --days 30
```

### Options

- `--mode`: Order fetching mode
  - `open_only` (default): Only orders with status != Complete
  - `time_based`: All orders within the time period
- `--days`: Number of days back to search (default: 90 for open_only, 30 for time_based)

---

## 📂 Output Files

Each run creates a timestamped folder with:

### Excel Report (`etsy_orders.xlsx`)
Multiple sheets:
- **Preview Requests**: Customers requesting design approval
- **MS - Needs Made**: New Magic Star designs
- **MS - Needs Updated**: Magic Star designs to modify
- **RR - Needs Made**: New Rainbow Runner designs
- **RR - Needs Updated**: Rainbow Runner designs to modify
- **Already Made**: Designs ready for production
- **Peace-Love-Hope Orders**: Special products
- **Other Orders**: Miscellaneous items
- **All Workflow Orders**: Complete summary

### CSV Files (for Adobe Illustrator)
- `illustrator_ms.csv`: Variable data for Magic Star batch
- `illustrator_rr.csv`: Variable data for Rainbow Runner batch

### Tracking Files
- `last_run_orders.json`: Order IDs for status tracking

---

## 🗂️ Project Structure

```
etsyorder_automation/
├── web_app.py              # Web interface (Streamlit)
├── main.py                 # Main automation script
├── etsy_api_connector.py   # Etsy API client
├── filename_generator.py   # Design filename generation
├── file_database.py        # Design file indexing
├── config.py               # Configuration settings
├── logger.py               # Logging setup
├── requirements.txt        # Python dependencies
├── .env                    # API credentials (create this)
├── etsy_tokens.json        # OAuth tokens (auto-generated)
├── start_web_app.sh        # Web app launcher (Mac/Linux)
├── start_web_app.bat       # Web app launcher (Windows)
└── README.md               # This file
```

---

## 🔧 Configuration

Edit `config.py` to customize:
- Database paths
- Output directories
- Workflow SKUs
- Processing settings

### Platform-Specific Paths

The system automatically detects your platform (Mac/Windows/Linux) and uses appropriate paths.

**Mac:**
- Database: `/Users/afakename/DocumentsMac/Snowflake_Database/Snowflake_Designs`
- Output: `/Users/afakename/DocumentsMac/Snowflake_Database/EtsyAutomation_Output`

**Windows:**
- Database: `C:/Users/tphov/Snowflake_Automation/Snowflake_Database/Snowflake_Designs`
- Output: `C:/Users/tphov/Snowflake_Automation/EtsyAutomation_Output`

---

## 🎯 Workflow

1. **Pull Orders**: Run automation via web app or CLI
2. **Review Preview Requests**: Check which customers want design approval
3. **Create Designs**: Use "Needs Made" lists and CSV files
4. **Update Designs**: Modify existing designs per "Needs Updated" lists
5. **Print & Ship**: Use "Already Made" list - designs are ready!

---

## 📊 Understanding Order Status

### File Status
- **Make**: Design needs to be created from scratch
- **Update**: Existing design needs modification (center or year change)
- **Exists**: Design already made and ready

### Order Status
- **New**: First time seeing this order
- **Previously Pulled**: Order was in a previous run

---

## 🚀 Advanced Features

### Preview Detection
Automatically detects preview requests from:
- Order variation selections ("Request Design Preview")
- Customer messages (keywords: preview, mockup, proof, approval)

### Smart Design Matching
- Exact filename matching for "Already Made"
- Intelligent update detection (center type, year changes)
- Handles case-insensitive variations

### Batch Processing
- Auto-generates CSV files for Illustrator variable data
- Creates slicer staging folders for 3D printing batches
- Organizes files by run timestamp

---

## 🛠️ Troubleshooting

### Authentication Issues
```bash
# Re-authenticate with Etsy
python etsy_api_connector.py
```

### Missing Orders
- Check `--days` parameter (increase if needed)
- Verify order status matches your mode (`open_only` vs `time_based`)

### Database Not Found
- Verify paths in `config.py` match your system
- Check that design files exist in the database folder

### Web App Won't Start
```bash
# Install dependencies manually
pip install -r requirements.txt

# Run directly
streamlit run web_app.py
```

---

## 📋 Requirements

- Python 3.8 or higher
- Internet connection (Etsy API)
- Etsy API credentials (Client ID & Secret)
- Modern web browser (for web interface)

---

## 🔐 Security Notes

- Never commit `.env` file to version control
- Keep `etsy_tokens.json` private
- Refresh tokens expire - re-authenticate periodically

---

## 📝 License

Private project for Etsy shop automation.

---

## 🤝 Support

For issues or questions:
1. Check this README
2. Review the [Web App Guide](WEB_APP_README.md)
3. Check log files in output folders
4. Verify Etsy API credentials

---

**Built with ❄️ for snowflake ornament production automation**
