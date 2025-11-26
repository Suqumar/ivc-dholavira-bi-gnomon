#!/bin/bash

# Optimize and Rename Photos for Dholavira Bi-Gnomon Project
# Uses macOS built-in tools only (sips, mdls)
#
# Usage:
#   ./optimize_and_rename.sh /path/to/input/folder /path/to/output/folder event-name
#
# Example:
#   ./optimize_and_rename.sh ~/Desktop/Dec22Photos ./images/solstice solstice
#   ./optimize_and_rename.sh ~/Desktop/EquinoxPhotos ./images/equinox equinox

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -ne 3 ]; then
    echo -e "${RED}❌ Error: Wrong number of arguments${NC}"
    echo "Usage: $0 <input_folder> <output_folder> <event_name>"
    echo ""
    echo "Examples:"
    echo "  $0 ~/Desktop/Dec22Photos ./images/solstice solstice"
    echo "  $0 ~/Desktop/EquinoxPhotos ./images/equinox equinox"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"
EVENT_NAME="$3"

# Validate input directory
if [ ! -d "$INPUT_DIR" ]; then
    echo -e "${RED}❌ Error: Input directory '$INPUT_DIR' does not exist${NC}"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Create backup directory for originals
BACKUP_DIR="${OUTPUT_DIR}_originals"
mkdir -p "$BACKUP_DIR"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📸 Dholavira Photo Optimizer${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Input:${NC}   $INPUT_DIR"
echo -e "${GREEN}Output:${NC}  $OUTPUT_DIR"
echo -e "${GREEN}Backup:${NC}  $BACKUP_DIR"
echo -e "${GREEN}Event:${NC}   $EVENT_NAME"
echo ""

# Settings
MAX_WIDTH=1920
QUALITY=82

# Counters
processed=0
failed=0
total_original_size=0
total_optimized_size=0

# Process each image file
shopt -s nullglob  # Handle case when no files match
for filepath in "$INPUT_DIR"/*.{jpg,jpeg,JPG,JPEG,png,PNG}; do
    [ -f "$filepath" ] || continue

    filename=$(basename "$filepath")
    echo -e "${YELLOW}Processing:${NC} $filename"

    # Get original file size
    original_size=$(stat -f%z "$filepath")
    total_original_size=$((total_original_size + original_size))

    # Get EXIF creation date using mdls (macOS metadata tool)
    # mdls returns format: 2022-12-22 06:15:30 +0000
    exif_date=$(mdls -name kMDItemContentCreationDate -raw "$filepath" 2>/dev/null)

    if [ "$exif_date" = "(null)" ] || [ -z "$exif_date" ]; then
        # Fallback to file modification date
        echo -e "  ${YELLOW}⚠️  No EXIF date found, using file modification date${NC}"
        timestamp=$(stat -f "%Sm" -t "%Y-%m-%d-%H%M" "$filepath")
    else
        # Parse EXIF date: "2022-12-22 06:15:30 +0000" -> "2022-12-22-0615"
        timestamp=$(echo "$exif_date" | awk '{print $1"-"substr($2,1,2)substr($2,4,2)}')
    fi

    # Generate new filename
    new_filename="${EVENT_NAME}-${timestamp}.jpg"
    output_path="$OUTPUT_DIR/$new_filename"

    # Handle duplicates by adding suffix
    counter=1
    while [ -f "$output_path" ]; do
        new_filename="${EVENT_NAME}-${timestamp}-${counter}.jpg"
        output_path="$OUTPUT_DIR/$new_filename"
        counter=$((counter + 1))
    done

    # Copy original to backup
    cp "$filepath" "$BACKUP_DIR/$filename"

    # Copy to output location first
    cp "$filepath" "$output_path"

    # Optimize using sips (macOS built-in image tool)
    sips --resampleWidth $MAX_WIDTH \
         --setProperty format jpeg \
         --setProperty formatOptions $QUALITY \
         "$output_path" &>/dev/null

    if [ $? -eq 0 ]; then
        optimized_size=$(stat -f%z "$output_path")
        total_optimized_size=$((total_optimized_size + optimized_size))

        # Calculate reduction
        reduction=$(awk "BEGIN {printf \"%.1f\", (1 - $optimized_size / $original_size) * 100}")
        original_mb=$(awk "BEGIN {printf \"%.1f\", $original_size / 1024 / 1024}")
        optimized_mb=$(awk "BEGIN {printf \"%.1f\", $optimized_size / 1024 / 1024}")

        echo -e "  ${GREEN}✅ $original_mb MB → $optimized_mb MB (${reduction}% reduction)${NC}"
        echo -e "  ${BLUE}→${NC}  $new_filename"

        processed=$((processed + 1))
    else
        echo -e "  ${RED}❌ Optimization failed${NC}"
        failed=$((failed + 1))
    fi

    echo ""
done

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Successfully processed: $processed photos${NC}"
if [ $failed -gt 0 ]; then
    echo -e "${RED}❌ Failed: $failed photos${NC}"
fi
echo ""
echo -e "${BLUE}📊 Storage Summary:${NC}"

original_gb=$(awk "BEGIN {printf \"%.2f\", $total_original_size / 1024 / 1024 / 1024}")
optimized_gb=$(awk "BEGIN {printf \"%.2f\", $total_optimized_size / 1024 / 1024 / 1024}")
saved_gb=$(awk "BEGIN {printf \"%.2f\", ($total_original_size - $total_optimized_size) / 1024 / 1024 / 1024}")
saved_percent=$(awk "BEGIN {printf \"%.1f\", (1 - $total_optimized_size / $total_original_size) * 100}")

echo -e "   Original total:  ${original_gb} GB"
echo -e "   Optimized total: ${optimized_gb} GB"
echo -e "   ${GREEN}Space saved:     ${saved_gb} GB (${saved_percent}% reduction)${NC}"
echo ""
echo -e "${BLUE}📁 Optimized photos:${NC} $OUTPUT_DIR"
echo -e "${BLUE}💾 Original backups:${NC} $BACKUP_DIR"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
