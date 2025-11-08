# file_database.py
import os
from pathlib import Path
import re
from logger import setup_logger
from config import Config

class FileDatabase:
    def __init__(self, logger=None):
        self.logger = logger or setup_logger("file_database")
        self.database_path = Config.get_database_path()
        self.file_index = {}
        self.scan_files()
    
    def scan_files(self):
        """Scan all year directories for SVG files"""
        if not self.database_path.exists():
            self.logger.error(f"Database path does not exist: {self.database_path}")
            return
        
        self.logger.info(f"Scanning files in: {self.database_path}")
        file_count = 0
        
        # Scan each year directory (excluding outdated 2021 and 2022)
        year_directories = [
            "2023 Snowflakes",
            "2024 Snowflakes",
            "2025 Snowflakes"
        ]
        
        for year_dir in year_directories:
            year_path = self.database_path / year_dir
            if year_path.exists():
                self.logger.info(f"Scanning {year_dir}...")
                year_count = 0
                
                for file_path in year_path.rglob("*.svg"):
                    filename = file_path.stem
                    self.file_index[filename.lower()] = file_path
                    year_count += 1
                    file_count += 1
                
                self.logger.info(f"Found {year_count} files in {year_dir}")
            else:
                self.logger.warning(f"Year directory not found: {year_path}")
        
        self.logger.info(f"Total indexed files: {file_count}")
    
    def find_file(self, target_filename):
        """Find a file with fuzzy matching"""
        # Direct match first
        if target_filename.lower() in self.file_index:
            return self.file_index[target_filename.lower()]

        # Fuzzy matching
        matches = self.fuzzy_search(target_filename)

        if matches:
            self.logger.info(f"Found fuzzy match for '{target_filename}': {matches[0].name}")
            return matches[0]

        self.logger.warning(f"No file found for: {target_filename}")
        return None

    def find_similar_file(self, target_filename):
        """Find a file with same name but different year/star - for 'Needs Updated' detection"""
        target_parts = self.extract_filename_parts(target_filename)

        for indexed_filename, file_path in self.file_index.items():
            indexed_parts = self.extract_filename_parts(indexed_filename)

            # Check if same name and design type, but different year/star
            if (target_parts['name'] == indexed_parts['name'] and
                target_parts['has_ms'] == indexed_parts['has_ms'] and
                target_parts['design'] == indexed_parts['design'] and
                target_parts['year'] != indexed_parts['year']):

                self.logger.info(f"Found similar file for '{target_filename}': {file_path.name} (different year/star)")
                return file_path

        return None
    
    def fuzzy_search(self, target_filename):
        """Search for files with similar names, preferring higher version numbers"""
        target_parts = self.extract_filename_parts(target_filename)

        matches = []
        for indexed_filename, file_path in self.file_index.items():
            indexed_parts = self.extract_filename_parts(indexed_filename)

            if self.is_similar_design(target_parts, indexed_parts):
                matches.append((file_path, indexed_parts['version']))

        # Sort by version number (higher first), then by filename
        matches.sort(key=lambda x: (x[1], x[0].name), reverse=True)

        # Return just the file paths
        return [match[0] for match in matches]
    
    def extract_filename_parts(self, filename):
        """
        Extract components from filename, handling:
        - Multi-word names (e.g., "Fuck This Ms Flk")
        - Version numbers (e.g., "Steve 2 Star" or "Steve2 Ms Flk")
        - Years (4 digits) vs versions (1-3 digits)

        Examples:
        - "Fuck This Ms Flk 2025" -> name: "fuck this", version: 0, year: "2025"
        - "Steve 2 Star" -> name: "steve", version: 2, year: ""
        - "Steve2 Ms Flk" -> name: "steve", version: 2, year: ""
        """
        parts = filename.lower().split()

        if not parts:
            return {'name': '', 'has_ms': False, 'design': '', 'year': '', 'version': 0}

        # Find where "ms" appears (if at all)
        ms_index = None
        for i, part in enumerate(parts):
            if part == 'ms':
                ms_index = i
                break

        # If "ms" found, everything before it is the name portion
        if ms_index is not None:
            name_parts = parts[:ms_index]
            remaining_parts = parts[ms_index:]
        else:
            # No "ms", find where design starts (star/flk)
            design_index = None
            for i, part in enumerate(parts):
                if part in ['star', 'flk', 'flake']:
                    design_index = i
                    break

            if design_index is not None:
                name_parts = parts[:design_index]
                remaining_parts = parts[design_index:]
            else:
                # No clear separator, assume first part is name
                name_parts = [parts[0]]
                remaining_parts = parts[1:]

        # Extract version number from name_parts
        # Check if last part of name is a 1-3 digit number (version)
        version = 0
        if name_parts:
            last_part = name_parts[-1]
            # Check if it's purely digits and 1-3 characters (version number)
            if last_part.isdigit() and 1 <= len(last_part) <= 3:
                version = int(last_part)
                name_parts = name_parts[:-1]  # Remove version from name

        # Join name parts
        name = ' '.join(name_parts)

        # Check for Ms indicator
        has_ms = 'ms' in parts

        # Find design type from remaining parts
        design = ''
        if any('star' in p for p in remaining_parts):
            design = 'star'
        elif any(term in ' '.join(remaining_parts) for term in ['flk', 'flake']):
            design = 'flk'

        # Find year (4-digit number) in remaining parts
        year = ''
        for part in remaining_parts:
            if part.isdigit() and len(part) == 4:
                year = part
                break

        return {
            'name': name,
            'has_ms': has_ms,
            'design': design,
            'year': year,
            'version': version
        }
    
    def is_similar_design(self, target_parts, indexed_parts):
        """Check if designs match"""
        return (
            target_parts['name'] == indexed_parts['name'] and
            target_parts['has_ms'] == indexed_parts['has_ms'] and
            target_parts['design'] == indexed_parts['design']
        )
    
    def get_version_number(self, filename):
        """Extract version number from filename"""
        match = re.search(r'\w+\s+(\d+)', str(filename))
        return int(match.group(1)) if match else 0