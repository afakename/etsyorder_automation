#!/usr/bin/env python3
"""
Test script to verify folder detection
"""

from file_database import FileDatabase
from logger import setup_logger

def test_folder_detection():
    """Test that all year folders are detected properly"""
    print("\n" + "="*70)
    print("TESTING FOLDER DETECTION")
    print("="*70)

    # Create logger
    logger = setup_logger("test")

    # Initialize file database (this will scan folders)
    print("\nInitializing FileDatabase...")
    db = FileDatabase(logger)

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Total files indexed: {len(db.file_index)}")

    # Show some sample files
    print("\nSample files found:")
    for i, (filename, path) in enumerate(list(db.file_index.items())[:10]):
        print(f"  {i+1}. {filename} -> {path.parent.name}")

    print("\n" + "="*70)
    print("✓ Folder detection test complete!")
    print("="*70)

if __name__ == "__main__":
    test_folder_detection()
