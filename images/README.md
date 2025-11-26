# Photo Gallery Setup Guide

This directory contains the photos for your bi-gnomon project galleries.

## Directory Structure

```
images/
├── equinox/    # Photos from equinox observations
└── solstice/   # Photos from solstice observations
```

## How to Add Photos

### Step 1: Upload Your Photos

1. Place your equinox photos in the `images/equinox/` directory
2. Place your solstice photos in the `images/solstice/` directory

**Supported formats**: JPG, PNG, WEBP

**Recommended naming**: Use descriptive names that include date and time:
- Examples: `equinox-2022-03-20-0600.jpg`, `solstice-2022-06-21-1200.jpg`

### Step 2: Update the Gallery Configuration

After uploading your photos, you need to add them to the gallery JavaScript code:

#### For Equinox Gallery

Edit `equinox-gallery.html` and find the `photos` array (around line 168):

```javascript
const photos = [
  { src: 'images/equinox/equinox-2022-03-20-0600.jpg', caption: 'Spring Equinox - 06:00 AM' },
  { src: 'images/equinox/equinox-2022-03-20-0615.jpg', caption: 'Spring Equinox - 06:15 AM' },
  { src: 'images/equinox/equinox-2022-03-20-0630.jpg', caption: 'Spring Equinox - 06:30 AM' },
  // Add more photos here...
];
```

#### For Solstice Gallery

Edit `solstice-gallery.html` and find the `photos` array (around line 168):

```javascript
const photos = [
  { src: 'images/solstice/solstice-2022-06-21-0600.jpg', caption: 'Summer Solstice - 06:00 AM' },
  { src: 'images/solstice/solstice-2022-06-21-0615.jpg', caption: 'Summer Solstice - 06:15 AM' },
  { src: 'images/solstice/solstice-2022-06-21-0630.jpg', caption: 'Summer Solstice - 06:30 AM' },
  // Add more photos here...
];
```

### Step 3: Commit and Push to GitHub

```bash
git add images/
git add equinox-gallery.html solstice-gallery.html
git commit -m "Add equinox and solstice photos to gallery"
git push origin main
```

GitHub Pages will automatically update your site within a few minutes.

## Gallery Features

- **Responsive grid layout**: Automatically adjusts to screen size
- **Lightbox viewer**: Click any photo to view full size
- **Keyboard navigation**: Use arrow keys to navigate, ESC to close
- **Touch-friendly**: Swipe on mobile devices
- **Lazy loading**: Photos load as you scroll for better performance

## Tips

1. **Optimize your photos** before uploading:
   - Recommended width: 1920px or less
   - Use JPG format with 80-85% quality for best balance of quality and file size
   - Tools: ImageOptim, TinyPNG, or Squoosh

2. **Organize chronologically**: List photos in time order in the array

3. **Clear captions**: Include date, time, and any relevant details

4. **Test locally**: If you're running a local server, test the gallery before pushing to GitHub

## Example: Full Setup

If you have these files in `images/equinox/`:
- `photo1.jpg`
- `photo2.jpg`
- `photo3.jpg`

Update `equinox-gallery.html`:

```javascript
const photos = [
  { src: 'images/equinox/photo1.jpg', caption: 'Spring Equinox - Dawn' },
  { src: 'images/equinox/photo2.jpg', caption: 'Spring Equinox - Noon' },
  { src: 'images/equinox/photo3.jpg', caption: 'Spring Equinox - Dusk' },
];
```

That's it! Your gallery is now ready to display your photos.
