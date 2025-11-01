#!/usr/bin/env python3
"""
SVG to STL/3MF Converter
Converts 2D SVG designs to 3D printable files with fixed dimensions.

Fixed parameters:
- Longest side (X or Y): 112mm
- Extrusion depth (Z): 3.8mm
- Aspect ratio: preserved
"""

import sys
import os
from pathlib import Path
import numpy as np
from xml.dom import minidom
import trimesh
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union
from shapely import affinity
from svgpathtools import svg2paths2, Path as SvgPath
import warnings

# Suppress shapely warnings about invalid geometries (we'll fix them)
warnings.filterwarnings('ignore', category=RuntimeWarning)

# Fixed dimensions
TARGET_LONGEST_SIDE_MM = 112.0
EXTRUSION_DEPTH_MM = 3.8


def parse_svg_to_shapes(svg_file):
    """
    Parse SVG file and extract all paths as Shapely geometries.
    Handles compound paths with holes.

    Returns:
        tuple: (list of shapely polygons, original width, original height)
    """
    print(f"📄 Reading SVG: {svg_file}")

    # Parse SVG paths
    paths, attributes, svg_attributes = svg2paths2(svg_file)

    # Get SVG viewBox or width/height
    # Handle different unit types (pt, px, mm, etc)
    viewbox = svg_attributes.get('viewBox', None)
    if viewbox:
        parts = viewbox.split()
        svg_width = float(parts[2])
        svg_height = float(parts[3])
    else:
        width_str = svg_attributes.get('width', '100')
        height_str = svg_attributes.get('height', '100')

        # Remove unit suffixes and convert
        svg_width = float(width_str.replace('pt', '').replace('px', '').replace('mm', ''))
        svg_height = float(height_str.replace('pt', '').replace('px', '').replace('mm', ''))

    print(f"  SVG dimensions: {svg_width:.2f} x {svg_height:.2f}")

    all_polygons = []

    for path_idx, (path, attr) in enumerate(zip(paths, attributes)):
        if len(path) == 0:
            continue

        # Convert path to polygon points
        # For intricate designs, we need MUCH denser sampling
        points = []
        num_samples = max(100, len(path) * 50)  # Increased sampling density

        for i in range(num_samples):
            t = i / (num_samples - 1)
            point = path.point(t)
            points.append((point.real, point.imag))

        if len(points) < 3:
            continue

        try:
            # Create polygon
            poly = Polygon(points)

            # Fix invalid geometries
            if not poly.is_valid:
                poly = poly.buffer(0)

            if poly.is_valid and not poly.is_empty:
                all_polygons.append(poly)
        except Exception as e:
            print(f"  ⚠️  Warning: Could not process path {path_idx}: {e}")
            continue

    print(f"  ✓ Extracted {len(all_polygons)} shapes")
    return all_polygons, svg_width, svg_height


def merge_and_handle_holes(polygons):
    """
    Merge overlapping polygons and handle holes properly.
    Uses unary_union to automatically handle complex overlaps and holes.

    Returns:
        MultiPolygon or Polygon: Unified geometry with holes preserved
    """
    print("🔄 Processing geometry and holes...")

    if not polygons:
        raise ValueError("No valid polygons found in SVG")

    # Union all polygons - this handles overlaps and holes automatically
    unified = unary_union(polygons)

    # Ensure we have valid geometry
    if not unified.is_valid:
        unified = unified.buffer(0)

    if isinstance(unified, Polygon):
        print(f"  ✓ Created unified shape with {len(unified.interiors)} hole(s)")
    elif isinstance(unified, MultiPolygon):
        total_holes = sum(len(p.interiors) for p in unified.geoms)
        print(f"  ✓ Created {len(unified.geoms)} separate shapes with {total_holes} total hole(s)")

    return unified


def scale_to_target_size(geometry, original_width, original_height):
    """
    Scale geometry so longest side is TARGET_LONGEST_SIDE_MM.

    Returns:
        Scaled geometry
    """
    print(f"📏 Scaling to target dimensions...")

    # Get actual geometry bounds (this is more reliable than SVG attributes)
    bounds = geometry.bounds  # (minx, miny, maxx, maxy)
    actual_width = bounds[2] - bounds[0]
    actual_height = bounds[3] - bounds[1]

    print(f"  SVG reported: {original_width:.2f} x {original_height:.2f}")
    print(f"  Actual geometry: {actual_width:.2f} x {actual_height:.2f}")

    # Determine which side is longest (use actual geometry bounds)
    longest_actual = max(actual_width, actual_height)
    scale_factor = TARGET_LONGEST_SIDE_MM / longest_actual

    # Calculate final dimensions
    final_width = actual_width * scale_factor
    final_height = actual_height * scale_factor

    print(f"  Scale factor: {scale_factor:.4f}")
    print(f"  Final: {final_width:.2f}mm x {final_height:.2f}mm x {EXTRUSION_DEPTH_MM}mm")

    # Scale the geometry
    scaled = affinity.scale(geometry, xfact=scale_factor, yfact=scale_factor, origin=(0, 0))

    return scaled


def polygon_to_3d_mesh(geometry):
    """
    Convert 2D Shapely geometry to 3D mesh with extrusion.
    Handles both Polygon and MultiPolygon with holes.

    Returns:
        trimesh.Trimesh: 3D mesh
    """
    print(f"🔨 Creating 3D mesh...")

    meshes = []

    # Handle both single Polygon and MultiPolygon
    if isinstance(geometry, Polygon):
        geoms = [geometry]
    elif isinstance(geometry, MultiPolygon):
        geoms = list(geometry.geoms)
    else:
        raise ValueError(f"Unexpected geometry type: {type(geometry)}")

    for poly in geoms:
        # Get exterior coordinates
        exterior_coords = np.array(poly.exterior.coords[:-1])  # Remove duplicate last point

        # Get interior (holes) coordinates
        holes = []
        for interior in poly.interiors:
            holes.append(np.array(interior.coords[:-1]))

        # Create the 2D polygon for extrusion
        if holes:
            # Create polygon with holes
            try:
                mesh = trimesh.creation.extrude_polygon(
                    poly,
                    height=EXTRUSION_DEPTH_MM
                )
                meshes.append(mesh)
            except Exception as e:
                print(f"  ⚠️  Warning: Could not extrude polygon with holes: {e}")
                # Fallback: try without holes
                simple_poly = Polygon(exterior_coords)
                mesh = trimesh.creation.extrude_polygon(
                    simple_poly,
                    height=EXTRUSION_DEPTH_MM
                )
                meshes.append(mesh)
        else:
            # Simple polygon without holes
            mesh = trimesh.creation.extrude_polygon(
                poly,
                height=EXTRUSION_DEPTH_MM
            )
            meshes.append(mesh)

    # Combine all meshes
    if len(meshes) == 1:
        final_mesh = meshes[0]
    else:
        final_mesh = trimesh.util.concatenate(meshes)

    print(f"  ✓ Created mesh with {len(final_mesh.vertices)} vertices, {len(final_mesh.faces)} faces")

    return final_mesh


def convert_svg_to_3d(svg_file, output_stl=None, output_3mf=None):
    """
    Main conversion function.

    Args:
        svg_file: Path to input SVG file
        output_stl: Path to output STL file (optional)
        output_3mf: Path to output 3MF file (optional)

    Returns:
        tuple: (stl_path, 3mf_path) - paths to generated files
    """
    svg_path = Path(svg_file)

    if not svg_path.exists():
        raise FileNotFoundError(f"SVG file not found: {svg_file}")

    # Default output paths
    if output_stl is None:
        output_stl = svg_path.with_suffix('.stl')
    if output_3mf is None:
        output_3mf = svg_path.with_suffix('.3mf')

    print(f"\n{'='*60}")
    print(f"SVG to 3D Converter")
    print(f"{'='*60}\n")

    # Step 1: Parse SVG
    polygons, svg_width, svg_height = parse_svg_to_shapes(svg_file)

    # Step 2: Merge and handle holes
    unified_geometry = merge_and_handle_holes(polygons)

    # Step 3: Scale to target size
    scaled_geometry = scale_to_target_size(unified_geometry, svg_width, svg_height)

    # Step 4: Convert to 3D mesh
    mesh = polygon_to_3d_mesh(scaled_geometry)

    # Step 5: Export to STL
    print(f"\n💾 Exporting files...")
    mesh.export(output_stl)
    print(f"  ✓ STL saved: {output_stl}")

    # Step 6: Export to 3MF
    mesh.export(output_3mf)
    print(f"  ✓ 3MF saved: {output_3mf}")

    print(f"\n{'='*60}")
    print(f"✅ Conversion complete!")
    print(f"{'='*60}\n")

    return str(output_stl), str(output_3mf)


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python converter.py <input.svg> [options]")
        print("\nOptions:")
        print("  --output-dir DIR    Save output files to specified directory")
        print("  output.stl          Specify STL output path")
        print("  output.3mf          Specify 3MF output path")
        print("\nExamples:")
        print("  python converter.py design.svg")
        print("  python converter.py design.svg --output-dir /path/to/output")
        print("  python converter.py design.svg output.stl output.3mf")
        sys.exit(1)

    svg_file = sys.argv[1]
    output_dir = None
    output_stl = None
    output_3mf = None

    # Parse arguments - check for options first
    args_remaining = []
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--output-dir' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            args_remaining.append(sys.argv[i])
            i += 1

    # Now parse remaining positional arguments
    if len(args_remaining) > 0:
        output_stl = args_remaining[0]
    if len(args_remaining) > 1:
        output_3mf = args_remaining[1]

    # Handle output directory
    svg_path = Path(svg_file)
    if output_dir:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        if output_stl is None:
            output_stl = output_dir_path / svg_path.with_suffix('.stl').name
        if output_3mf is None:
            output_3mf = output_dir_path / svg_path.with_suffix('.3mf').name

    # Ensure paths are Path objects if specified
    if output_stl and not isinstance(output_stl, Path):
        output_stl = Path(output_stl)
    if output_3mf and not isinstance(output_3mf, Path):
        output_3mf = Path(output_3mf)

    try:
        convert_svg_to_3d(svg_file, output_stl, output_3mf)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
