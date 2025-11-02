# Mac Automator Quick Action Setup

Create a right-click menu option to convert SVG files directly from Finder.

## Setup Instructions

### 1. Open Automator

- Open **Automator** (found in Applications folder or use Spotlight)
- Choose **Quick Action** (or "Service" in older macOS versions)

### 2. Configure Workflow Settings

At the top of the workflow:
- **Workflow receives current:** `files or folders`
- **in:** `Finder`
- **Image:** (optional) Choose an icon
- **Color:** (optional) Choose a color

### 3. Add "Run Shell Script" Action

1. Search for "Run Shell Script" in the actions library (left panel)
2. Drag it to the workflow area (right panel)
3. Configure the action:
   - **Shell:** `/bin/bash`
   - **Pass input:** `as arguments`

4. **Paste this script:**

```bash
#!/bin/bash

# Path to your converter (UPDATE THIS PATH!)
CONVERTER_PATH="/Users/afakename/path/to/etsyorder_automation/svg_to_stl_converter"

# Activate virtual environment and run converter
cd "$CONVERTER_PATH"
source venv/bin/activate

# Process each selected file
for file in "$@"; do
    if [[ "$file" == *.svg ]]; then
        python converter.py "$file"

        # Show notification (optional)
        osascript -e "display notification \"Converted: $(basename "$file")\" with title \"SVG to STL Converter\""
    else
        osascript -e "display notification \"Skipped: $(basename "$file") (not an SVG)\" with title \"SVG to STL Converter\""
    fi
done

# Final notification
osascript -e "display notification \"All files processed\" with title \"SVG to STL Converter\" sound name \"Glass\""
```

⚠️ **IMPORTANT:** Update the `CONVERTER_PATH` variable to match your actual path!

### 4. Save the Quick Action

1. Go to **File → Save** (or press ⌘S)
2. Name it: **"Convert SVG to STL"**
3. Save location: Automator will automatically save it to `~/Library/Services/`

### 5. Test It

1. Find any SVG file in Finder
2. Right-click (or Control-click) on the file
3. Look for **Quick Actions → Convert SVG to STL**
4. Click it!

The converter will run and create `.stl` and `.3mf` files in the same directory as your SVG.

## Usage Tips

### Converting Multiple Files

- Select multiple SVG files in Finder
- Right-click on the selection
- Choose **Quick Actions → Convert SVG to STL**
- All files will be processed in sequence

### Notifications

The workflow will show macOS notifications:
- When each file is converted
- When all files are complete
- If a non-SVG file is skipped

### Troubleshooting

#### Quick Action doesn't appear in menu

1. Go to **System Preferences → Extensions → Finder**
2. Make sure "Convert SVG to STL" is checked
3. Or go to **System Preferences → Keyboard → Shortcuts → Services**
4. Find and enable "Convert SVG to STL"

#### Permission errors

1. Open **System Preferences → Security & Privacy → Privacy**
2. Select **Automation** (left panel)
3. Make sure Automator has permissions for Finder and System Events

#### Script fails to run

1. Open the Quick Action in Automator (**File → Open**)
2. Location: `~/Library/Services/Convert SVG to STL.workflow`
3. Click **Run** button in Automator to see error messages
4. Check that the `CONVERTER_PATH` is correct
5. Verify virtual environment exists: `ls "$CONVERTER_PATH/venv"`

## Alternative: Droplet Method

If you prefer a drag-and-drop icon on your Desktop:

### Create Droplet Script

1. Create file: `~/Desktop/SVG_to_STL_Droplet.command`

2. Contents:
```bash
#!/bin/bash
cd /Users/afakename/path/to/etsyorder_automation/svg_to_stl_converter
source venv/bin/activate

for file in "$@"; do
    python converter.py "$file"
done

echo "✅ Conversion complete!"
read -p "Press Enter to close..."
```

3. Make executable:
```bash
chmod +x ~/Desktop/SVG_to_STL_Droplet.command
```

4. **Usage:** Drag SVG files onto the `SVG_to_STL_Droplet.command` icon

### Custom Icon (Optional)

1. Find an icon image (PNG or ICNS file)
2. Open the image file in Preview
3. Press ⌘A (Select All), then ⌘C (Copy)
4. Right-click `SVG_to_STL_Droplet.command` → Get Info
5. Click the icon in top-left of the info window
6. Press ⌘V (Paste)

## Keyboard Shortcut (Optional)

Add a keyboard shortcut for even faster access:

1. **System Preferences → Keyboard → Shortcuts → Services**
2. Find "Convert SVG to STL" in the list
3. Click "Add Shortcut"
4. Press your desired key combination (e.g., ⌃⌘S)

Now you can:
1. Select SVG file in Finder
2. Press your keyboard shortcut
3. Instant conversion!

## Uninstall

To remove the Quick Action:

```bash
rm ~/Library/Services/Convert\ SVG\ to\ STL.workflow
```

Or use Finder:
1. Go to `~/Library/Services/`
2. Delete "Convert SVG to STL.workflow"
