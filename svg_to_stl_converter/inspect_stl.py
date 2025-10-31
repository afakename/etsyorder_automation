#!/usr/bin/env python3
"""
Diagnostic tool to inspect STL/3MF files and check dimensions
"""

import sys
import trimesh

if len(sys.argv) < 2:
    print("Usage: python inspect_stl.py <file.stl>")
    sys.exit(1)

mesh_file = sys.argv[1]

print(f"\n{'='*60}")
print(f"Inspecting: {mesh_file}")
print(f"{'='*60}\n")

try:
    mesh = trimesh.load(mesh_file)

    print(f"📊 Mesh Statistics:")
    print(f"  Vertices: {len(mesh.vertices):,}")
    print(f"  Faces: {len(mesh.faces):,}")
    print(f"  Watertight: {mesh.is_watertight}")
    print(f"  Volume: {mesh.volume:.2f} cubic units")
    print()

    print(f"📏 Dimensions:")
    dims = mesh.extents
    print(f"  X: {dims[0]:.2f} mm")
    print(f"  Y: {dims[1]:.2f} mm")
    print(f"  Z: {dims[2]:.2f} mm")
    print(f"  Longest side: {max(dims[0], dims[1]):.2f} mm")
    print()

    print(f"📍 Bounding Box:")
    print(f"  Min: [{mesh.bounds[0][0]:.2f}, {mesh.bounds[0][1]:.2f}, {mesh.bounds[0][2]:.2f}]")
    print(f"  Max: [{mesh.bounds[1][0]:.2f}, {mesh.bounds[1][1]:.2f}, {mesh.bounds[1][2]:.2f}]")
    print()

    print(f"✓ Expected dimensions: ~112mm × ~110mm × 3.8mm")

    # Check if dimensions are way off
    longest = max(dims[0], dims[1])
    if longest > 200:
        print(f"\n⚠️  WARNING: Longest side is {longest:.2f}mm (expected 112mm)")
        print(f"   Model is {longest/112:.1f}x too large!")
    elif longest < 50:
        print(f"\n⚠️  WARNING: Longest side is {longest:.2f}mm (expected 112mm)")
        print(f"   Model is {112/longest:.1f}x too small!")

    if dims[2] > 10 or dims[2] < 1:
        print(f"\n⚠️  WARNING: Z height is {dims[2]:.2f}mm (expected 3.8mm)")

    print(f"\n{'='*60}\n")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
