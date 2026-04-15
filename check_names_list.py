#!/usr/bin/env python3
# check_names_list.py - Process a list of names and check file database
import sys
import argparse
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

            # Check if the year/design matches
            target_parts = self.file_database.extract_filename_parts(filename)
            match_parts = self.file_database.extract_filename_parts(best_match_filename)

            # If year or design is different, this needs to be made as a new variant
            if target_parts['year'] != match_parts['year']:
                self.logger.info(f"Year mismatch: target has '{target_parts['year']}', match has '{match_parts['year']}' - needs to be MADE")
                return 'make', None, f"Found {best_match_filename} but different year"
            elif target_parts['design'] != match_parts['design']:
                self.logger.info(f"Design mismatch: target has '{target_parts['design']}', match has '{match_parts['design']}' - needs to be MADE")
                return 'make', None, f"Found {best_match_filename} but different design"

            # Year and design match, it's the same design
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

            # If name already has "Star" or "Flk" at the end, strip it
            # (some names come as "Mark Star" already)
            if name.endswith(' Star') or name.endswith(' star'):
                name = name.rsplit(' ', 1)[0]
            elif name.endswith(' Flk') or name.endswith(' flk') or name.endswith(' Flake') or name.endswith(' flake'):
                name = name.rsplit(' ', 1)[0]

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

    def generate_report(self, results, product_type='RR'):
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

        # Generate Illustrator CSV for items that need made
        csv_file = self.generate_illustrator_csv(results['needs_made'], product_type)

        return output_file, csv_file

    def generate_illustrator_csv(self, needs_made, product_type):
        """Generate Illustrator CSV for items that need to be made"""
        if not needs_made:
            self.logger.info("No items need made - skipping CSV generation")
            return None

        if product_type == 'RR':
            # RR CSV format: Name, Center, Preview
            csv_data = []
            for item in needs_made:
                # Use preserved center/year/preview info if available
                center = item.get('center', 'Star')
                preview = item.get('preview', 'no')
                # For RR with years, the center column should contain the year
                csv_data.append({
                    'Name': item['sanitized_name'],
                    'Center': center,  # Use original center value (could be year or "Star")
                    'Preview': preview  # Use original preview value
                })

            df = pd.DataFrame(csv_data)
            csv_file = self.output_folder / 'illustrator_rr.csv'
            df.to_csv(csv_file, index=False)
            self.logger.info(f"RR Illustrator CSV generated: {csv_file}")
            return csv_file
        elif product_type == 'MS':
            # MS CSV format: Name, Center, Year, Preview
            csv_data = []
            for item in needs_made:
                # Use preserved center/year/preview info if available
                center = item.get('center', 'Star')
                year = item.get('year', 'No')
                preview = item.get('preview', 'no')
                csv_data.append({
                    'Name': item['sanitized_name'],
                    'Center': center,  # Use original center value
                    'Year': year if year else 'No',  # Use original year value
                    'Preview': preview  # Use original preview value
                })

            df = pd.DataFrame(csv_data)
            csv_file = self.output_folder / 'illustrator_ms.csv'
            df.to_csv(csv_file, index=False)
            self.logger.info(f"MS Illustrator CSV generated: {csv_file}")
            return csv_file

        return None

    def run_with_metadata(self, names_with_info, product_type):
        """
        Process names with metadata from Illustrator CSV format.

        Args:
            names_with_info: List of dicts with 'name', 'center', optionally 'year'
            product_type: 'RR' or 'MS'
        """
        try:
            print(f"\n{'='*60}")
            print(f"Name List Checker (Illustrator Format)")
            print(f"{'='*60}")
            print(f"Processing {len(names_with_info)} names...")
            print(f"Product Type: {product_type}")
            print(f"{'='*60}\n")

            results = {
                'needs_made': [],
                'needs_updated': [],
                'already_made': []
            }

            for item in names_with_info:
                name = item['name']
                center = item.get('center', 'Star')
                year = item.get('year')
                preview = item.get('preview', 'no')

                # Sanitize name
                sanitized_name = self.filename_generator.sanitize_name(name)

                # Generate filename based on metadata
                if product_type == 'MS':
                    if year:
                        filename = f"{sanitized_name} MS {center} {year}"
                    else:
                        filename = f"{sanitized_name} MS {center}"
                else:  # RR
                    # RR is always Star, year implies star
                    # Check if center is actually a year (numeric like "2025")
                    if year:
                        filename = f"{sanitized_name} {year}"
                    elif center and center.isdigit() and len(center) == 4:
                        # Center column contains a year
                        filename = f"{sanitized_name} {center}"
                    else:
                        filename = f"{sanitized_name} Star"

                self.logger.info(f"Checking: {name} -> {filename}")

                # Check file status
                status, file_path, update_details = self.check_file_status(filename)

                result_data = {
                    'original_name': name,
                    'sanitized_name': sanitized_name,
                    'generated_filename': filename,
                    'status': status,
                    'file_path': str(file_path) if file_path else 'NOT FOUND',
                    'update_details': update_details if update_details else '',
                    'center': center,  # Preserve original center/year info
                    'year': year,
                    'preview': preview  # Preserve original preview value
                }

                if status == 'make':
                    results['needs_made'].append(result_data)
                elif status == 'update':
                    results['needs_updated'].append(result_data)
                else:
                    result_data['days_since_modified'] = self.get_days_since_modified(file_path)
                    results['already_made'].append(result_data)

            # Generate report
            output_file, csv_file = self.generate_report(results, product_type)

            # Print summary
            print(f"\n{'='*60}")
            print(f"RESULTS SUMMARY")
            print(f"{'='*60}")
            print(f"Needs Made: {len(results['needs_made'])}")
            print(f"Needs Updated: {len(results['needs_updated'])}")
            print(f"Already Made: {len(results['already_made'])}")
            print(f"{'='*60}")
            print(f"\nExcel Report saved to:")
            print(f"{output_file}")
            if csv_file:
                print(f"\nIllustrator CSV saved to:")
                print(f"{csv_file}")
            print(f"{'='*60}\n")

            self.logger.info("Name check completed successfully")

        except Exception as e:
            self.logger.error(f"Name check failed: {e}")
            raise

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
            output_file, csv_file = self.generate_report(results, product_type)

            # Print summary
            print(f"\n{'='*60}")
            print(f"RESULTS SUMMARY")
            print(f"{'='*60}")
            print(f"Needs Made: {len(results['needs_made'])}")
            print(f"Needs Updated: {len(results['needs_updated'])}")
            print(f"Already Made: {len(results['already_made'])}")
            print(f"{'='*60}")
            print(f"\nExcel Report saved to:")
            print(f"{output_file}")
            if csv_file:
                print(f"\nIllustrator CSV saved to:")
                print(f"{csv_file}")
            print(f"{'='*60}\n")

            self.logger.info("Name check completed successfully")

        except Exception as e:
            self.logger.error(f"Name check failed: {e}")
            raise


def read_names_from_csv(csv_path):
    """
    Read names from a CSV file.

    CSV can be in multiple formats:
    1. Illustrator RR format: Name, Center, Preview
    2. Illustrator MS format: Name, Center, Year, Preview
    3. Simple list (one name per line, no header)
    4. CSV with 'Name' column header

    Returns: (names_list, detected_type, detected_center_info)
        - names_list: list of name strings or dicts with metadata
        - detected_type: 'RR', 'MS', or None
        - detected_center_info: dict with center/year info per name or None
    """
    csv_file = Path(csv_path)

    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    try:
        df = pd.read_csv(csv_file)

        # Check for Illustrator format
        columns_lower = [col.lower() for col in df.columns]

        has_name = 'name' in columns_lower
        has_center = 'center' in columns_lower
        has_year = 'year' in columns_lower
        has_preview = 'preview' in columns_lower

        if has_name and has_center:
            # This is Illustrator format!
            name_col = df.columns[columns_lower.index('name')]
            center_col = df.columns[columns_lower.index('center')]

            if has_year:
                # MS format (Name, Center, Year, Preview)
                year_col = df.columns[columns_lower.index('year')]
                preview_col = df.columns[columns_lower.index('preview')] if has_preview else None
                detected_type = 'MS'

                names_with_info = []
                for idx, row in df.iterrows():
                    name = row[name_col]
                    center = row[center_col]
                    year = row[year_col]
                    preview = row[preview_col] if preview_col else 'no'

                    if pd.isna(name):
                        continue

                    # Normalize preview value: "yes", "preview", or variations → "Preview", otherwise "no"
                    preview_normalized = 'no'
                    if not pd.isna(preview):
                        preview_str = str(preview).strip().lower()
                        if preview_str in ['yes', 'preview', 'y']:
                            preview_normalized = 'Preview'

                    names_with_info.append({
                        'name': str(name).strip(),
                        'center': str(center).strip() if not pd.isna(center) else 'Star',
                        'year': str(year).strip() if not pd.isna(year) and str(year).strip().lower() not in ['no', 'none', ''] else None,
                        'preview': preview_normalized
                    })

                return names_with_info, detected_type, True
            else:
                # RR format (Name, Center, Preview)
                detected_type = 'RR'
                preview_col = df.columns[columns_lower.index('preview')] if has_preview else None

                names_with_info = []
                for idx, row in df.iterrows():
                    name = row[name_col]
                    center = row[center_col]
                    preview = row[preview_col] if preview_col else 'no'

                    if pd.isna(name):
                        continue

                    # Normalize preview value: "yes", "preview", or variations → "Preview", otherwise "no"
                    preview_normalized = 'no'
                    if not pd.isna(preview):
                        preview_str = str(preview).strip().lower()
                        if preview_str in ['yes', 'preview', 'y']:
                            preview_normalized = 'Preview'

                    names_with_info.append({
                        'name': str(name).strip(),
                        'center': str(center).strip() if not pd.isna(center) else 'Star',
                        'preview': preview_normalized
                    })

                return names_with_info, detected_type, True

        # Not Illustrator format - look for Name column
        name_col = None
        for col in df.columns:
            if col.lower() == 'name':
                name_col = col
                break

        if name_col:
            names = df[name_col].dropna().tolist()
        else:
            # Assume first column is names
            names = df.iloc[:, 0].dropna().tolist()

        return [str(n).strip() for n in names], None, False

    except:
        # If pandas fails, read as plain text
        with open(csv_file, 'r') as f:
            names = [line.strip() for line in f if line.strip()]

        return names, None, False


def main():
    """Entry point with command-line argument support"""
    parser = argparse.ArgumentParser(
        description='Check a list of names against the file database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use a CSV file
  python check_names_list.py --csv my_names.csv

  # Specify product type and center
  python check_names_list.py --csv my_names.csv --type MS --center Flk

  # Use the hardcoded list (default if no CSV provided)
  python check_names_list.py

CSV Format:
  The CSV can be:
  - Simple list (one name per line)
  - CSV with "Name" column header
  - CSV where first column contains names
        '''
    )

    parser.add_argument('--csv', type=str, help='Path to CSV file with names')
    parser.add_argument('--type', type=str, choices=['RR', 'MS'], default=None,
                       help='Product type: RR or MS (auto-detected from Illustrator CSV, defaults to RR)')
    parser.add_argument('--center', type=str, choices=['Star', 'Flk'], default=None,
                       help='Center design: Star or Flk (auto-detected from Illustrator CSV, defaults to Star). Note: RR is always Star.')

    args = parser.parse_args()

    # Get names list
    detected_type = None
    detected_info = False

    if args.csv:
        # Read from CSV file
        print(f"Reading names from: {args.csv}")
        names_list, detected_type, detected_info = read_names_from_csv(args.csv)

        if detected_info:
            print(f"✓ Detected Illustrator {detected_type} format")
    else:
        # Use hardcoded list (fallback for when I update it)
        names_list = """
David
Mason
Blaine
Isaiah
Anthony
Kyle
Mark
Paul
Aiden
Kolbie
Richard
Tyrone
Everett
Finn
Kylee
Malia
Lida
Marissa
Rachel
Lacey
Lindsay
Skylar
Melanie
Katelyn
ChloeAnne
Lucia
""".strip().split('\n')
        detected_type = None
        detected_info = False

    # Determine product type and center
    product_type = args.type or detected_type or 'RR'
    center = args.center or 'Star'

    # Create checker and run
    checker = NameListChecker()

    if detected_info:
        # Illustrator format - process with metadata
        checker.run_with_metadata(names_list, product_type)
    else:
        # Simple list - process normally
        checker.run(names_list, product_type=product_type, center=center)


if __name__ == "__main__":
    main()
