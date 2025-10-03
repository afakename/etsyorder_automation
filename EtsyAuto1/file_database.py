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
        
        # Scan each year directory
        year_directories = [
            "2021 Snowflakes", "2022 Snowflakes", "2023 Snowflakes", 
            "2024 Snowflakes", "2025 Snowflakes"
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
    
    def fuzzy_search(self, target_filename):
        """Search for files with similar names"""
        target_parts = self.extract_filename_parts(target_filename)
        
        matches = []
        for indexed_filename, file_path in self.file_index.items():
            indexed_parts = self.extract_filename_parts(indexed_filename)
            
            if self.is_similar_design(target_parts, indexed_parts):
                matches.append(file_path)
        
        # Sort by version number (higher first)
        matches.sort(key=lambda x: self.get_version_number(x.name), reverse=True)
        return matches
    
    def extract_filename_parts(self, filename):
        """Extract components from filename"""
        parts = filename.lower().split()
        
        return {
            'name': parts[0] if parts else '',
            'has_ms': 'ms' in parts,
            'design': 'star' if any('star' in p for p in parts) else 'flk' if any(term in ' '.join(parts) for term in ['flk', 'flake']) else '',
            'year': next((p for p in parts if p.isdigit()), ''),
            'version': self.get_version_number(filename)
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