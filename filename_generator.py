# filename_generator.py
from datetime import datetime
from logger import setup_logger
import re

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
        """
        Generate MS ornament filename: {Name} Ms {Design} {Year}
        Handles "Choose the Center Piece" variation which can be:
        - "Star"
        - "Flake"
        - "Current Year" 
        - "Flake w/Current Year"
        - "Star w/2024" (or other specific year)
        - "Flake w/2024" (or other specific year)
        """
        center_piece = variations.get('Choose the Center Piece', 'Star')
        
        # Parse the center piece selection
        center_lower = center_piece.lower()
        
        # Determine design and year from center piece
        if 'flake' in center_lower or 'flk' in center_lower:
            design = 'Flk'
        else:
            design = 'Star'
        
        # Determine year
        if 'current year' in center_lower:
            year = self.get_current_year()
        elif re.search(r'\d{4}', center_piece):
            # Extract explicit year like "2024"
            year_match = re.search(r'\d{4}', center_piece)
            year = year_match.group(0)
        else:
            year = ''
        
        # Build filename
        parts = [name, 'Ms', design]
        if year:
            parts.append(str(year))
        
        filename = ' '.join(parts)
        self.logger.info(f"Generated MS filename: {filename} (from center piece: '{center_piece}')")
        return filename
    
    def generate_regular_filename(self, name, variations):
        """
        Generate RR ornament filename: {Name} {Year or Star}
        Handles "Choose the Center Piece" variation which can be:
        - "Star Design"
        - "Current Year"
        - Specific year like "2024"
        """
        center_piece = variations.get('Choose the Center Piece', 'Star')
        center_lower = center_piece.lower()
        
        # Handle dynamic year for RR variants
        if 'current year' in center_lower:
            year_or_star = self.get_current_year()
        elif 'star' in center_lower:
            year_or_star = 'Star'
        elif re.search(r'\d{4}', center_piece):
            # Extract explicit year
            year_match = re.search(r'\d{4}', center_piece)
            year_or_star = year_match.group(0)
        else:
            # Default to star if unclear
            year_or_star = 'Star'
        
        filename = f"{name} {year_or_star}"
        self.logger.info(f"Generated RR filename: {filename} (from center piece: '{center_piece}')")
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