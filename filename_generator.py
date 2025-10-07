# filename_generator.py
from datetime import datetime
from logger import setup_logger

class FilenameGenerator:
    def __init__(self, logger=None):
        self.logger = logger or setup_logger("filename_generator")
        
        self.sku_mapping = {
            "PerSnoFlkOrn-MS-01": {"type": "MS", "format": "{name} Ms {design} {year}"},
            "PerSnoFlkOrn-MS-02": {"type": "MS", "format": "{name} Ms {design} {year}"},
            "PerSnoFlkOrn-RR-01": {"type": "RR", "format": "{name} {year_or_star}"},
            "PerSnoFlkOrn-RR-02": {"type": "RR", "format": "{name} {year_or_star}"},
            "PerSnoFlkOrn-RR-03": {"type": "RR", "format": "{name} {year_or_star}"},
            "PerSnoFlkOrn-RR-04": {"type": "RR", "format": "{name} {year_or_star}"},
            "PerSnoFlkOrn-RR-05": {"type": "RR", "format": "{name} {year_or_star}"},
            "PerSnoFlkOrn-RR-06": {"type": "RR", "format": "{name} {year_or_star}"},
        }
    
    def get_current_year(self):
        """Get the current year dynamically"""
        return str(datetime.now().year)
    
    def generate_filename(self, transaction):
        """Generate filename from transaction data"""
        sku = transaction.get('sku', '')
        
        if sku not in self.sku_mapping:
            self.logger.warning(f"Unknown SKU: {sku}")
            return None
        
        # Extract variation data
        variations = self.extract_variations(transaction.get('variations', []))
        name = variations.get('Personalization', 'Unknown')
        
        product_info = self.sku_mapping[sku]
        
        if product_info["type"] == "MS":
            return self.generate_ms_filename(name, variations)
        else:
            return self.generate_regular_filename(name, variations)
    
    def extract_variations(self, variations_list):
        """Extract variation data into a clean dict"""
        variations = {}
        for var in variations_list:
            formatted_name = var.get('formatted_name', '')
            formatted_value = var.get('formatted_value', '')
            variations[formatted_name] = formatted_value
        return variations
    
    def generate_ms_filename(self, name, variations):
        """Generate MS ornament filename: {Name} Ms {Design} {Year}"""
        design_raw = variations.get('Choose the Center Piece', 'Star')
        year_raw = variations.get('Year or No Year', '')
        
        # Normalize design
        design = self.normalize_design(design_raw)
        
        # Handle year dynamically
        if 'current year' in year_raw.lower():
            year = self.get_current_year()  # Converts "Current Year" to actual year
        elif year_raw.lower() in ['no year', '']:
            year = ''
        else:
            # It's already a specific year like "2024"
            year = year_raw
        
        # Build filename
        parts = [name, 'Ms', design]
        if year:
            parts.append(str(year))
        
        filename = ' '.join(parts)
        self.logger.info(f"Generated MS filename: {filename}")
        return filename
    
    def generate_regular_filename(self, name, variations):
        """Generate regular ornament filename: {Name} {Year or Star}"""
        year_or_star_raw = variations.get('Current Year or Star Design', 'Star')
        
        # Handle dynamic year for RR variants
        if 'current year' in year_or_star_raw.lower():
            year_or_star = self.get_current_year()
        elif 'star' in year_or_star_raw.lower():
            year_or_star = 'Star'
        else:
            # Already a specific year
            year_or_star = year_or_star_raw
        
        filename = f"{name} {year_or_star}"
        self.logger.info(f"Generated regular filename: {filename}")
        return filename
    
    def normalize_design(self, design_raw):
        """Normalize design variations to standard format"""
        design_lower = design_raw.lower()
        
        if 'star' in design_lower:
            return 'Star'
        elif any(term in design_lower for term in ['flake', 'flk']):
            return 'Flk'
        else:
            return design_raw  # Return as-is if unknown