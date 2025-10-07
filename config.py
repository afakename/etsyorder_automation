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
    
    @classmethod
    def get_database_path(cls):
        """Get the appropriate database path for the current platform"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return Path("/Users/afakename/DocumentsMac/Snowflake_Database/Snowflake_Designs")
        elif system == "Windows":
            return Path("C:/Users/tphov/Snowflake_Automation/Snowflake_Database/Snowflake_Designs")
        else:
            return Path.home() / "Snowflake_Database" / "Snowflake_Designs"
    
    @classmethod 
    def get_output_path(cls):
        """Get platform-appropriate output directory"""
        system = platform.system()
        
        if system == "Darwin":
            return Path("/Users/afakename/DocumentsMac/Snowflake_Database/EtsyAutomation_Output")
        elif system == "Windows":
            return Path("C:/Users/tphov/Snowflake_Automation/EtsyAutomation_Output")
        else:
            return Path.home() / "Documents" / "EtsyAutomation" / "Output"
    
    @classmethod
    def get_log_path(cls):
        """Get platform-appropriate log directory"""
        system = platform.system()
        
        if system == "Darwin":
            return Path("/Users/afakename/Documents/EtsyAutomation/Logs")
        elif system == "Windows":
            return Path("C:/Users/tphov/Snowflake_Automation/Logs")
        else:
            return Path.home() / "Documents" / "EtsyAutomation" / "Logs"
    
    # Processing settings
    DAYS_BACK_DEFAULT = 7
    MAX_ORDERS_PROCESS = 100