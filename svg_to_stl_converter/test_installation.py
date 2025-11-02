#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly.
Run this after installing requirements.txt
"""

import sys

print("Testing SVG to STL Converter Installation")
print("=" * 60)

required_packages = {
    'trimesh': 'trimesh',
    'svgpathtools': 'svgpathtools',
    'shapely': 'shapely',
    'numpy': 'numpy',
}

all_ok = True

for package_name, import_name in required_packages.items():
    try:
        __import__(import_name)
        print(f"✅ {package_name:20s} - OK")
    except ImportError as e:
        print(f"❌ {package_name:20s} - MISSING")
        all_ok = False

print("=" * 60)

if all_ok:
    print("\n🎉 All dependencies installed successfully!")
    print("\nYou're ready to convert SVG files!")
    print("\nTry it:")
    print("  python converter.py your_design.svg")
else:
    print("\n⚠️  Some dependencies are missing.")
    print("\nTo install, run:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
