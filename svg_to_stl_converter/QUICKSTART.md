# Quick Start Guide

Get up and running in 5 minutes!

## 1. Setup (One-Time)

Open Terminal and run:

```bash
cd /path/to/etsyorder_automation/svg_to_stl_converter
bash setup_mac.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Test the installation

## 2. Convert Your First SVG

### Test with example file:
```bash
python converter.py examples/test_snowflake.svg
```

### Convert your own file:
```bash
python converter.py "/Users/afakename/DocumentsMac/Snowflake_Database/Snowflake_Designs/Snowflake SVGs/Annette ms flk 2025.svg"
```

## 3. Find Your Output Files

The converter creates two files in the same directory as your SVG:
- `filename.stl` - For most 3D slicers
- `filename.3mf` - Alternative format

## Output Dimensions

Every file will be:
- **Longest side:** 112mm
- **Thickness:** 3.8mm
- **Aspect ratio:** Preserved

## Common Commands

### Activate virtual environment (if not already active):
```bash
cd /path/to/etsyorder_automation/svg_to_stl_converter
source venv/bin/activate
```

### Convert a file:
```bash
python converter.py your_design.svg
```

### Convert multiple files:
```bash
python converter.py design1.svg
python converter.py design2.svg
python converter.py design3.svg
```

### Custom output location:
```bash
python converter.py input.svg /path/to/output.stl /path/to/output.3mf
```

## Next Steps

- **Drag-and-drop setup:** See `AUTOMATOR_SETUP.md`
- **Full documentation:** See `README.md`
- **Issues?** Check the troubleshooting section in `README.md`

## Pro Tips

1. **Keep virtual environment active** while converting multiple files
2. **Use absolute paths** if files aren't in the current directory
3. **Batch convert** by writing a simple loop script
4. **Check output** in your slicer software to verify dimensions

Happy printing! 🎉
