# config.py
import os
import platform
from pathlib import Path

class Config:
    # API Configuration
    ETSY_CLIENT_ID = os.getenv("ETSY_CLIENT_ID", "1bsfw0s4klwjm2hvie9zb4cr")
    ETSY_CLIENT_SECRET = os.getenv("ETSY_CLIENT_SECRET")
    TOKEN_FILE = "etsy_tokens.json"
    
    # Workflow SKUs
    WORKFLOW_SKUS = [
        "PerSnoFlkOrn-MS-01", "PerSnoFlkOrn-MS-02",
        "PerSnoFlkOrn-RR-01", "PerSnoFlkOrn-RR-02", 
        "PerSnoFlkOrn-RR-03", "PerSnoFlkOrn-RR-04",
        "PerSnoFlkOrn-RR-05", "PerSnoFlkOrn-RR-06"
    ]
    
    # Platform-specific paths
    @classmethod
    def get_database_path(cls):
        """Get the appropriate database path for the current platform"""
        system = platform.system()
    
        if system == "Darwin":  # macOS
            return Path("/Users/afakename/DocumentsMac/Snowflake_Database/Snowflake_Designs")
        elif system == "Windows":
        # ... rest of Windows code stays the same
            # Check multiple possible locations on Windows
            locations = [
                Path("//your-mac-name/Snowflakes Database"),  # Network share
                Path("D:/Snowflakes Database"),  # External drive
                Path.home() / "Documents" / "Snowflakes Database"  # Local copy
            ]
            for location in locations:
                if location.exists():
                    return location
            return locations[-1]  # Return local path as default
        else:
            return Path.home() / "Snowflakes Database"
    
    @classmethod 
    @classmethod 
    def get_output_path(cls):
        """Get platform-appropriate output directory"""
        if platform.system() == "Darwin":  # macOS
            return Path("/Users/afakename/DocumentsMac/Snowflake_Database/EtsyAutomation_Output")
        else:
            return Path.home() / "Documents" / "EtsyAutomation" / "Output"
    
    @classmethod
    def get_log_path(cls):
        """Get platform-appropriate log directory"""  
        return Path.home() / "Documents" / "EtsyAutomation" / "Logs"
    
    # Processing settings
    DAYS_BACK_DEFAULT = 7
    MAX_ORDERS_PROCESS = 100