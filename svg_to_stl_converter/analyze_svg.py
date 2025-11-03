#!/usr/bin/env python3
"""
Analyze SVG path structure to understand compound paths
"""

import sys
from svgpathtools import svg2paths2

if len(sys.argv) < 2:
    print("Usage: python analyze_svg.py <file.svg>")
    sys.exit(1)

svg_file = sys.argv[1]

print(f"Analyzing: {svg_file}\n")

# Read the SVG
paths, attrs, svg_attrs = svg2paths2(svg_file)

print(f"Number of path elements: {len(paths)}")
print(f"SVG attributes: {list(svg_attrs.keys())}\n")

for idx, (path, attr) in enumerate(zip(paths, attrs)):
    print(f"Path {idx}:")
    print(f"  Segments: {len(path)}")
    print(f"  Continuous: {path.iscontinuous()}")
    print(f"  Closed: {path.isclosed()}")

    # Check for discontinuities (separate sub-paths)
    discontinuities = []
    for i in range(len(path)-1):
        if abs(path[i].end - path[i+1].start) > 0.01:
            discontinuities.append(i)

    if discontinuities:
        print(f"  ⚠️  Contains {len(discontinuities)+1} discontinuous sub-paths!")
        print(f"  This means holes/cutouts are embedded in this single path")

    # Check attributes for fill-rule
    if 'fill-rule' in attr:
        print(f"  Fill rule: {attr['fill-rule']}")

    print()
