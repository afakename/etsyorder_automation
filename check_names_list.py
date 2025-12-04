#!/usr/bin/env python3
# check_names_list.py - Process a list of names and check file database
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
from config import Config
from logger import setup_logger
from filename_generator import FilenameGenerator
from file_database import FileDatabase

class NameListChecker:
    def __init__(self):
        # Set up logging
        Config.get_log_path().mkdir(parents=True, exist_ok=True)

        # Create timestamped run folder
        self.run_timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        self.output_folder = Config.get_output_path() / f"name_check_{self.run_timestamp}"
        self.output_folder.mkdir(parents=True, exist_ok=True)

        log_file = self.output_folder / "name_check.log"
        self.logger = setup_logger("name_check", log_file)

        self.logger.info("=" * 50)
        self.logger.info(f"Starting Name List Check - Run: {self.run_timestamp}")
        self.logger.info("=" * 50)

        # Initialize components
        self.filename_generator = FilenameGenerator(self.logger)
        self.file_database = FileDatabase(self.logger)

    def normalize_filename(self, filename):
        """Normalize filename for comparison"""
        normalized = filename.lower()
        normalized = ' '.join(normalized.split())
        normalized = normalized.replace('flake', 'flk')
        return normalized

    def check_file_status(self, filename):
        """
        Check if design needs to be made, updated, or already exists.
        Same logic as main.py
        """
        # Step 1: Check for EXACT match
        normalized_search = self.normalize_filename(filename)

        for indexed_filename, file_path in self.file_database.file_index.items():
            if self.normalize_filename(indexed_filename) == normalized_search:
                # Skip files from 2021 and 2022
                if self.file_database.is_file_too_old(file_path):
                    self.logger.info(f"Skipping old exact match from 2021/2022: {indexed_filename}")
                    continue

                self.logger.info(f"EXACT MATCH found: {indexed_filename}")
                return 'exists', file_path, None

        # Step 2: Use fuzzy search (version-aware, excludes 2021-2022)
        fuzzy_matches = self.file_database.fuzzy_search(filename)

        if fuzzy_matches:
            # Get the highest version match
            best_match = fuzzy_matches[0]
            best_match_filename = best_match.stem

            self.logger.info(f"FUZZY MATCH found: {best_match_filename} (highest version)")

            # For "Name Star" variants, center is always 'star' and no year
            # So if we find a match, it's the same design
            self.logger.info(f"MATCH found (version {self.file_database.get_version_number(best_match_filename)}): {best_match_filename}")
            return 'exists', best_match, None

        # Step 3: No matches found
        self.logger.info(f"NO MATCH found for: {filename} - needs to be MADE")
        return 'make', None, None

    def get_days_since_modified(self, file_path):
        """Calculate days since file was last modified"""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return 'N/A'

            modified_time = datetime.fromtimestamp(file_path_obj.stat().st_mtime)
            days_ago = (datetime.now() - modified_time).days
            return days_ago
        except Exception as e:
            self.logger.warning(f"Could not get modified time for {file_path}: {e}")
            return 'N/A'

    def process_names(self, names_list, product_type='RR', center='Star'):
        """
        Process a list of names and check file database.

        Args:
            names_list: List of name strings
            product_type: 'RR' or 'MS' (default: 'RR')
            center: 'Star' or 'Flk' (default: 'Star')
        """
        results = {
            'needs_made': [],
            'needs_updated': [],
            'already_made': []
        }

        for name in names_list:
            name = name.strip()
            if not name:
                continue

            # Skip comments or special notes
            if '(' in name and ')' in name:
                # Extract the actual name part
                self.logger.info(f"Processing special name: {name}")
                # For "John Jackie (if possible)", just use "John Jackie"
                name = name.split('(')[0].strip()

            # Sanitize the name (normalize caps, remove spaces)
            sanitized_name = self.filename_generator.sanitize_name(name)

            # Generate filename based on product type
            if product_type == 'MS':
                # MS format: "Name MS Center Year"
                # For this use case, we'll assume no year for now
                filename = f"{sanitized_name} MS {center}"
            else:
                # RR format: "Name Center"
                filename = f"{sanitized_name} {center}"

            self.logger.info(f"Checking: {name} -> {filename}")

            # Check file status
            status, file_path, update_details = self.check_file_status(filename)

            result_data = {
                'original_name': name,
                'sanitized_name': sanitized_name,
                'generated_filename': filename,
                'status': status,
                'file_path': str(file_path) if file_path else 'NOT FOUND',
                'update_details': update_details if update_details else ''
            }

            if status == 'make':
                results['needs_made'].append(result_data)
            elif status == 'update':
                results['needs_updated'].append(result_data)
            else:
                # Add days since modified for already made
                result_data['days_since_modified'] = self.get_days_since_modified(file_path)
                results['already_made'].append(result_data)

        return results

    def generate_report(self, results):
        """Generate Excel report with results"""
        output_file = self.output_folder / "name_check_results.xlsx"

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Needs Made sheet
            if results['needs_made']:
                df_make = pd.DataFrame([{
                    'Original Name': item['original_name'],
                    'Sanitized Name': item['sanitized_name'],
                    'Generated Filename': item['generated_filename'],
                    'Status': 'NEEDS MADE'
                } for item in results['needs_made']])
                df_make.to_excel(writer, sheet_name='Needs Made', index=False)

            # Needs Updated sheet (probably won't have any for simple "Name Star" variants)
            if results['needs_updated']:
                df_update = pd.DataFrame([{
                    'Original Name': item['original_name'],
                    'Sanitized Name': item['sanitized_name'],
                    'Generated Filename': item['generated_filename'],
                    'Status': 'NEEDS UPDATED',
                    'Update Details': item['update_details']
                } for item in results['needs_updated']])
                df_update.to_excel(writer, sheet_name='Needs Updated', index=False)

            # Already Made sheet with file paths
            if results['already_made']:
                df_made = pd.DataFrame([{
                    'Original Name': item['original_name'],
                    'Sanitized Name': item['sanitized_name'],
                    'Generated Filename': item['generated_filename'],
                    'File Path': item['file_path'],
                    'Days Since Modified': item['days_since_modified'],
                    'Status': 'ALREADY MADE'
                } for item in results['already_made']])
                df_made.to_excel(writer, sheet_name='Already Made', index=False)

                # Add hyperlinks to file paths
                worksheet = writer.sheets['Already Made']
                file_path_col = df_made.columns.get_loc('File Path') + 1
                for idx in range(len(df_made)):
                    file_path = df_made.iloc[idx]['File Path']
                    if file_path != 'NOT FOUND':
                        cell = worksheet.cell(row=idx+2, column=file_path_col)
                        cell.hyperlink = file_path
                        cell.style = 'Hyperlink'

        self.logger.info(f"Report generated: {output_file}")
        return output_file

    def run(self, names_list, product_type='RR', center='Star'):
        """Main execution"""
        try:
            print(f"\n{'='*60}")
            print(f"Name List Checker")
            print(f"{'='*60}")
            print(f"Processing {len(names_list)} names...")
            print(f"Product Type: {product_type}")
            print(f"Center Design: {center}")
            print(f"{'='*60}\n")

            # Process names
            results = self.process_names(names_list, product_type, center)

            # Generate report
            output_file = self.generate_report(results)

            # Print summary
            print(f"\n{'='*60}")
            print(f"RESULTS SUMMARY")
            print(f"{'='*60}")
            print(f"Needs Made: {len(results['needs_made'])}")
            print(f"Needs Updated: {len(results['needs_updated'])}")
            print(f"Already Made: {len(results['already_made'])}")
            print(f"{'='*60}")
            print(f"\nReport saved to:")
            print(f"{output_file}")
            print(f"{'='*60}\n")

            self.logger.info("Name check completed successfully")

        except Exception as e:
            self.logger.error(f"Name check failed: {e}")
            raise


def main():
    """Entry point"""
    # List of names to check
    names_list = """
Atwell
Brunette
Dellas
Davis
DeFrain
Dellas
Dunigan
Harton
Higdon
Huntzinger
Baumann
Sibrt
Norris
Siegfried
Timmerman
John Jackie (if possible)
Christiano
Harmes
Kenney
Riede
Lalomia
Tooley
Pahl
Jones
Brown
Soren Tracy (if possible)
Renner
Sutton
Anderson
Olfier
Craft
Leeth
Scott
Minteer
Bearman
Sycks
Variell
McAndrew
Gates
Kreklau
Crowder
Kloer
Waugh
Bowden
Ziegler
Mangones
Town
Malak
Blunt
Wright
Fenger
Ecker
Mangones
MacFarlane
Mooney
Mohney
Budan
Kampf
Fenger
Carlson
Nally
Henry
Hoop
Peters
""".strip().split('\n')

    # Create checker and run
    checker = NameListChecker()
    checker.run(names_list, product_type='RR', center='Star')


if __name__ == "__main__":
    main()
