#!/bin/bash
# Automatic sync script for Snowflake designs to iCloud

SOURCE="/Users/afakename/DocumentsMac/Snowflake_Database/Snowflake_Designs"
DEST="/Users/afakename/Library/Mobile Documents/com~apple~CloudDocs/Documents/DocumentsMini/Snowflake_Database"

# Get current year
YEAR=$(date +%Y)

# Sync the current year's folder
echo "Syncing ${YEAR} Snowflakes to iCloud..."
rsync -av --delete "${SOURCE}/${YEAR} Snowflakes/" "${DEST}/${YEAR} Snowflakes/"

# Also sync the Snowflake SVGs folder
echo "Syncing Snowflake SVGs to iCloud..."
rsync -av --delete "${SOURCE}/Snowflake SVGs/" "${DEST}/Snowflake SVGs/"

echo "Sync completed at $(date)"