import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime
import platform

def create_slicer_staging_folder(excel_file_path=None):
    """
    Copy 'Already Made' files to a staging folder for batch processing in slicer
    """
    
    # Determine paths based on platform
    system = platform.system()
    if system == "Windows":
        staging_folder = Path("C:/Users/tphov/Snowflake_Automation/Slicer_Ready")
        output_base = Path("C:/Users/tphov/Snowflake_Automation/EtsyAutomation_Output")
    else:  # macOS
        staging_folder = Path("/Users/afakename/DocumentsMac/Snowflake_Database/Slicer_Ready")
        output_base = Path("/Users/afakename/DocumentsMac/Snowflake_Database/EtsyAutomation_Output")
    
    # Find the most recent Excel file if not specified
    if excel_file_path is None:
        excel_files = sorted(output_base.glob("etsy_orders_*.xlsx"), reverse=True)
        if not excel_files:
            print("No Excel files found in output folder")
            return
        excel_file_path = excel_files[0]
    
    print(f"Processing: {excel_file_path.name}")
    
    # Read the 'Already Made' sheet
    try:
        df = pd.read_excel(excel_file_path, sheet_name='Already Made')
    except ValueError:
        print("No 'Already Made' sheet found in Excel file")
        return
    
    if df.empty:
        print("No files in 'Already Made' sheet")
        return
    
    # Create timestamped staging folder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    batch_folder = staging_folder / f"batch_{timestamp}"
    batch_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"\nCreating staging folder: {batch_folder}")
    print("=" * 60)
    
    copied_count = 0
    missing_count = 0
    
    # Copy each file to staging folder
    for idx, row in df.iterrows():
        file_path = Path(row['File Path'])
        
        if not file_path.exists():
            print(f"❌ Missing: {file_path.name}")
            missing_count += 1
            continue
        
        # Copy to staging folder
        destination = batch_folder / file_path.name
        shutil.copy2(file_path, destination)
        copied_count += 1
        print(f"✓ Copied: {file_path.name}")
    
    print("=" * 60)
    print(f"\nBatch Processing Summary:")
    print(f"  Files copied: {copied_count}")
    print(f"  Missing files: {missing_count}")
    print(f"\nStaging folder location:")
    print(f"  {batch_folder}")
    print(f"\nYou can now drag all files from this folder into Bambu Studio")
    
    # Create a batch info file
    info_file = batch_folder / "_batch_info.txt"
    with open(info_file, 'w') as f:
        f.write(f"Batch created: {datetime.now()}\n")
        f.write(f"Source Excel: {excel_file_path.name}\n")
        f.write(f"Files copied: {copied_count}\n")
        f.write(f"Missing files: {missing_count}\n\n")
        f.write("Files in this batch:\n")
        for file in sorted(batch_folder.glob("*.svg")):
            f.write(f"  - {file.name}\n")
    
    return batch_folder

if __name__ == "__main__":
    # Run the staging folder creation
    staging_path = create_slicer_staging_folder()
    
    if staging_path:
        print("\nNext steps:")
        print("1. Open the staging folder above")
        print("2. Select all SVG files (Ctrl+A or Cmd+A)")
        print("3. Drag them into Bambu Studio")
        print("4. Delete the staging folder when done printing")