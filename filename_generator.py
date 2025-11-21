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
<<<<<<< Updated upstream
    
=======

    def smart_capitalize_name(self, name):
        """
        Intelligently capitalize names, remove spaces and punctuation:
        - Convert ALL CAPS to title case (JESUS -> Jesus, LILY MAE -> LilyMae)
        - Preserve mixed case names (McCarthy, DrAdams, MacQueen)
        - Remove all spaces (Lily Mae -> LilyMae, Phil Linda -> PhilLinda)
        - Remove punctuation (Dr. Marshall -> DrMarshall, Baby M. -> BabyM)
        """
        # If the name is empty or None, return it as-is
        if not name or not name.strip():
            return name

        name = name.strip()

        # Check if name is ALL CAPS (all letters are uppercase)
        # We check if it's all uppercase AND has at least one letter
        if name.isupper() and any(c.isalpha() for c in name):
            # Convert to title case
            name = name.title()

        # Remove all punctuation (periods, commas, apostrophes, etc.)
        name = re.sub(r'[^\w\s]', '', name)

        # Remove ALL whitespace (spaces, newlines, tabs, etc)
        name = re.sub(r'\s+', '', name)

        return name

>>>>>>> Stashed changes
    def generate_filename(self, transaction):
        """Generate filename from transaction data"""
        sku = transaction.get('sku', '')

        if sku not in self.sku_mapping:
            self.logger.warning(f"Unknown SKU: {sku}")
            return None

        # Extract variation data
        variations = self.extract_variations(transaction.get('variations', []))
<<<<<<< Updated upstream
        name = variations.get('Personalization', 'Unknown')

        # Log the exact personalization received for debugging
        self.logger.debug(f"Personalization received from Etsy: '{name}' (length: {len(name)}, repr: {repr(name)})")

        # Preserve the name exactly as provided by Etsy, including all punctuation
        # Common punctuation in names: apostrophes ('), hyphens (-), periods (.)
        # These are all safe for filenames on Windows, macOS, and Linux
=======
        name_raw = variations.get('Personalization', 'Unknown')

        # Apply smart capitalization and space removal
        name = self.smart_capitalize_name(name_raw)
>>>>>>> Stashed changes

        product_info = self.sku_mapping[sku]

        if product_info["type"] == "MS":
            return self.generate_ms_filename(name, variations)
        else:
            return self.generate_regular_filename(name, variations)

    def extract_variations(self, variations_list):
        """Extract variation data into a clean dict with case-insensitive keys"""
        variations = {}
        for var in variations_list:
            formatted_name = var.get('formatted_name', '')
            formatted_value = var.get('formatted_value', '')

            # Normalize the key to handle Etsy's inconsistent capitalization
            # "Choose the Center Piece" vs "choose the center piece"
            if formatted_name.lower() == 'choose the center piece':
                variations['Choose the Center Piece'] = formatted_value
            else:
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
        center_piece = variations.get('Choose the Center Piece', None)

        # DEBUG: Log what we received
        self.logger.info(f"DEBUG - MS Name: '{name}'")
        self.logger.info(f"DEBUG - Center Piece value: '{center_piece}'")
        self.logger.info(f"DEBUG - All variations: {variations}")

        # If no center piece found, log warning and default to Star
        if center_piece is None:
            self.logger.warning(f"No 'Choose the Center Piece' variation found for {name}, defaulting to Star")
            center_piece = 'Star'

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

        # Build filename with spaces between components
        parts = [name, 'Ms', design]
        if year:
            parts.append(str(year))

        filename = ' '.join(parts)  # Join WITH spaces between components
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
        center_piece = variations.get('Choose the Center Piece', None)

        # DEBUG: Log what we received (both to log and console)
        print(f"\n=== RR PROCESSING ===")
        print(f"Name: '{name}'")
        print(f"Center Piece variation: '{center_piece}'")
        print(f"All variations: {variations}")
        print(f"===================\n")

        self.logger.info(f"DEBUG - RR Name: '{name}'")
        self.logger.info(f"DEBUG - RR Center Piece value: '{center_piece}'")
        self.logger.info(f"DEBUG - RR All variations: {variations}")

        # If no center piece found, log warning and default to Star
        if center_piece is None:
            print(f"⚠️  WARNING: No 'Choose the Center Piece' variation found for {name}, defaulting to Star")
            self.logger.warning(f"No 'Choose the Center Piece' variation found for {name}, defaulting to Star")
            center_piece = 'Star'

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

        filename = f"{name} {year_or_star}"  # Space between name and year/star
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