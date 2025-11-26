#!/usr/bin/env python3
"""
Photo Optimization and Renaming Script for Dholavira Bi-Gnomon Project

This script:
1. Reads EXIF timestamps from photos
2. Renames files with format: event-YYYY-MM-DD-HHMM.jpg
3. Resizes to web-friendly dimensions (1920px width)
4. Compresses to 80-85% quality
5. Preserves original EXIF data
6. Keeps originals in a backup folder

Usage:
    python3 optimize_photos.py --input /path/to/photos --output ./images/solstice --event solstice
    python3 optimize_photos.py --input /path/to/photos --output ./images/equinox --event equinox

Requirements:
    pip3 install Pillow piexif
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image
import piexif

def get_exif_datetime(image_path):
    """Extract datetime from EXIF data."""
    try:
        exif_dict = piexif.load(str(image_path))

        # Try different EXIF datetime tags
        datetime_tags = [
            piexif.ExifIFD.DateTimeOriginal,
            piexif.ExifIFD.DateTimeDigitized,
        ]

        for tag in datetime_tags:
            if tag in exif_dict.get("Exif", {}):
                datetime_str = exif_dict["Exif"][tag].decode('utf-8')
                # EXIF format: "YYYY:MM:DD HH:MM:SS"
                dt = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
                return dt

        # Fallback to file modification time
        print(f"  ⚠️  No EXIF datetime found for {image_path.name}, using file modification time")
        mtime = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mtime)

    except Exception as e:
        print(f"  ⚠️  Error reading EXIF from {image_path.name}: {e}")
        # Fallback to file modification time
        mtime = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mtime)

def optimize_image(input_path, output_path, max_width=1920, quality=82):
    """Resize and compress image while preserving EXIF."""
    try:
        # Open image
        img = Image.open(input_path)

        # Get original EXIF data
        try:
            exif_bytes = piexif.dump(piexif.load(str(input_path)))
        except:
            exif_bytes = None

        # Calculate new dimensions
        width, height = img.size
        if width > max_width:
            ratio = max_width / width
            new_width = max_width
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to RGB if necessary (for PNG with transparency, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Save optimized image
        save_kwargs = {
            'quality': quality,
            'optimize': True,
            'progressive': True,
        }
        if exif_bytes:
            save_kwargs['exif'] = exif_bytes

        img.save(output_path, 'JPEG', **save_kwargs)

        return True
    except Exception as e:
        print(f"  ❌ Error optimizing {input_path.name}: {e}")
        return False

def process_photos(input_dir, output_dir, event_name, max_width=1920, quality=82):
    """Process all photos in input directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Create backup directory for originals
    backup_path = output_path.parent / f"{output_path.name}_originals"
    backup_path.mkdir(parents=True, exist_ok=True)

    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

    # Get all image files
    image_files = [f for f in input_path.iterdir()
                   if f.is_file() and f.suffix in image_extensions]

    if not image_files:
        print(f"❌ No image files found in {input_dir}")
        return

    print(f"\n📸 Found {len(image_files)} photos to process")
    print(f"📁 Output directory: {output_path}")
    print(f"💾 Backup directory: {backup_path}")
    print(f"🎯 Event name: {event_name}")
    print(f"📏 Max width: {max_width}px")
    print(f"🎨 Quality: {quality}%\n")

    # Process each file
    processed = 0
    failed = 0
    total_original_size = 0
    total_optimized_size = 0

    for img_file in sorted(image_files):
        try:
            # Get datetime from EXIF
            dt = get_exif_datetime(img_file)

            # Generate new filename: event-YYYY-MM-DD-HHMM.jpg
            new_filename = f"{event_name}-{dt.strftime('%Y-%m-%d-%H%M')}.jpg"
            output_file = output_path / new_filename

            # Check if file already exists, add suffix if needed
            counter = 1
            while output_file.exists():
                new_filename = f"{event_name}-{dt.strftime('%Y-%m-%d-%H%M')}-{counter}.jpg"
                output_file = output_path / new_filename
                counter += 1

            # Get original file size
            original_size = img_file.stat().st_size
            total_original_size += original_size

            # Optimize and save
            print(f"Processing: {img_file.name} → {new_filename}")
            if optimize_image(img_file, output_file, max_width, quality):
                optimized_size = output_file.stat().st_size
                total_optimized_size += optimized_size

                reduction = (1 - optimized_size / original_size) * 100
                print(f"  ✅ {original_size/1024/1024:.1f} MB → {optimized_size/1024/1024:.1f} MB ({reduction:.1f}% reduction)")

                # Copy original to backup
                backup_file = backup_path / img_file.name
                import shutil
                shutil.copy2(img_file, backup_file)

                processed += 1
            else:
                failed += 1

        except Exception as e:
            print(f"  ❌ Error processing {img_file.name}: {e}")
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Successfully processed: {processed} photos")
    if failed > 0:
        print(f"❌ Failed: {failed} photos")
    print(f"\n📊 Storage Summary:")
    print(f"   Original total: {total_original_size/1024/1024/1024:.2f} GB")
    print(f"   Optimized total: {total_optimized_size/1024/1024/1024:.2f} GB")
    print(f"   Space saved: {(total_original_size - total_optimized_size)/1024/1024/1024:.2f} GB ({(1-total_optimized_size/total_original_size)*100:.1f}% reduction)")
    print(f"\n📁 Optimized photos: {output_path}")
    print(f"💾 Original backups: {backup_path}")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(
        description='Optimize and rename photos for Dholavira Bi-Gnomon gallery',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 optimize_photos.py --input ~/Desktop/Dec22Photos --output ./images/solstice --event solstice
  python3 optimize_photos.py --input ~/Desktop/EquinoxPhotos --output ./images/equinox --event equinox --width 2560
        """
    )

    parser.add_argument('--input', '-i', required=True,
                        help='Input directory containing photos')
    parser.add_argument('--output', '-o', required=True,
                        help='Output directory for optimized photos')
    parser.add_argument('--event', '-e', required=True,
                        choices=['solstice', 'equinox', 'winter-solstice', 'summer-solstice', 'spring-equinox', 'fall-equinox'],
                        help='Event name for filename prefix')
    parser.add_argument('--width', '-w', type=int, default=1920,
                        help='Maximum width in pixels (default: 1920)')
    parser.add_argument('--quality', '-q', type=int, default=82,
                        help='JPEG quality 1-100 (default: 82)')

    args = parser.parse_args()

    # Validate inputs
    if not os.path.isdir(args.input):
        print(f"❌ Error: Input directory '{args.input}' does not exist")
        sys.exit(1)

    if args.quality < 1 or args.quality > 100:
        print(f"❌ Error: Quality must be between 1 and 100")
        sys.exit(1)

    # Process photos
    process_photos(args.input, args.output, args.event, args.width, args.quality)

if __name__ == '__main__':
    main()
