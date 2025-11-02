# SVG to STL/3MF Converter

Automated converter for transforming 2D SVG designs into 3D-printable STL and 3MF files with fixed dimensions.

## Features

- ✅ Converts complex SVG paths and curves to 3D meshes
- ✅ Preserves holes and cutouts in compound paths
- ✅ Fixed dimensions for consistent 3D printing:
  - Longest side (X or Y): **112mm**
  - Extrusion depth (Z): **3.8mm**
  - Aspect ratio: **preserved**
- ✅ Outputs both STL and 3MF formats
- ✅ Handles multiple shapes in one SVG
- ✅ Preserves fine details and curves

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup on Mac

1. **Open Terminal**

2. **Navigate to the converter directory:**
   ```bash
   cd /path/to/etsyorder_automation/svg_to_stl_converter
   ```

3. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

That's it! You're ready to convert SVG files.

## Usage

### Command Line

#### Basic usage (outputs to same directory as input):
```bash
python converter.py /path/to/your/design.svg
```

This will create:
- `design.stl`
- `design.3mf`

#### Specify output paths:
```bash
python converter.py input.svg output.stl output.3mf
```

### Examples

```bash
# Convert a snowflake design
python converter.py "/Users/afakename/DocumentsMac/Snowflake_Database/Snowflake_Designs/Snowflake SVGs/Annette ms flk 2025.svg"

# Convert and specify custom output location
python converter.py design.svg /path/to/output/design.stl /path/to/output/design.3mf
```

## Drag-and-Drop Setup (Mac)

### Method 1: Droplet Application

1. **Create a shell script:**
   ```bash
   nano ~/Desktop/svg_to_stl.command
   ```

2. **Paste this content:**
   ```bash
   #!/bin/bash
   cd /path/to/etsyorder_automation/svg_to_stl_converter
   source venv/bin/activate
   python converter.py "$@"
   ```

3. **Make it executable:**
   ```bash
   chmod +x ~/Desktop/svg_to_stl.command
   ```

4. **Usage:** Drag SVG file(s) onto the `svg_to_stl.command` icon on your Desktop

### Method 2: Mac Automator Quick Action

See `AUTOMATOR_SETUP.md` for detailed instructions on creating a right-click menu option.

## Output Specifications

Every converted file will have these exact dimensions:

| Parameter | Value |
|-----------|-------|
| Longest side (X or Y) | 112mm |
| Shorter side | Proportionally scaled |
| Extrusion depth (Z) | 3.8mm |

### Example Dimensions:

- **Square design (100x100)** → 112mm x 112mm x 3.8mm
- **Wide design (200x100)** → 112mm x 56mm x 3.8mm
- **Tall design (100x200)** → 56mm x 112mm x 3.8mm

## Technical Details

### Supported SVG Features

- ✅ Complex paths and curves
- ✅ Compound paths
- ✅ Holes and cutouts
- ✅ Multiple separate shapes
- ✅ Filled shapes
- ✅ Outlined shapes

### Processing Steps

1. **Parse SVG:** Reads all paths from the SVG file
2. **Extract shapes:** Converts Bezier curves to polygons with dense sampling
3. **Handle holes:** Uses boolean operations to preserve cutouts
4. **Scale:** Proportionally scales to 112mm longest side
5. **Extrude:** Creates solid 3.8mm depth
6. **Export:** Saves as STL and 3MF

### Libraries Used

- **trimesh:** 3D mesh creation and export
- **svgpathtools:** SVG path parsing
- **shapely:** 2D geometry operations and hole handling
- **numpy:** Numerical operations

## Troubleshooting

### "Command not found: python"
Try using `python3` instead:
```bash
python3 converter.py design.svg
```

### Import errors
Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

### SVG not converting properly
- Ensure SVG is saved with paths (not raster images)
- Try opening the SVG in a vector editor and "Object to Path" if needed
- Check that the SVG has valid viewBox or width/height attributes

### Holes not appearing in output
- The script uses Shapely's unary_union which automatically handles holes
- If holes aren't showing, they may not be properly defined as compound paths in the SVG
- Try re-exporting the SVG with "compound path" option

## Advanced Usage

### Using in Python Scripts

```python
from converter import convert_svg_to_3d

# Convert a single file
stl_path, mf3_path = convert_svg_to_3d(
    "input.svg",
    output_stl="output.stl",
    output_3mf="output.3mf"
)

print(f"Created: {stl_path} and {mf3_path}")
```

### Batch Processing

Create a script to convert multiple files:

```bash
#!/bin/bash
for svg in /path/to/svgs/*.svg; do
    python converter.py "$svg"
done
```

## Future Integration

This converter is designed to eventually integrate with the full Etsy automation workflow. For now, it works as a standalone tool that you can run manually on your designs before uploading them.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed correctly
3. Verify your SVG file is valid vector format

## License

Part of the Etsy Order Automation project.
