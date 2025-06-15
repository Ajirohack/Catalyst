#!/bin/bash

# Create icon directory if it doesn't exist
mkdir -p "/Volumes/Project Disk/Catalyst/chrome_extension/icons"

# Copy the 16x16 icon
cp "/Volumes/Project Disk/Catalyst/catalyst_icon_pack/catalyst_icon_16x16.png" "/Volumes/Project Disk/Catalyst/chrome_extension/icons/icon16.png"

# Copy the 48x48 icon
cp "/Volumes/Project Disk/Catalyst/catalyst_icon_pack/catalyst_icon_48x48.png" "/Volumes/Project Disk/Catalyst/chrome_extension/icons/icon48.png"

# Copy the 128x128 icon
cp "/Volumes/Project Disk/Catalyst/catalyst_icon_pack/catalyst_icon_128x128.png" "/Volumes/Project Disk/Catalyst/chrome_extension/icons/icon128.png"

# Create a 32x32 icon (not present in the pack, so we'll use the 48x48 one and resize it)
# This requires ImageMagick to be installed
if command -v convert >/dev/null 2>&1; then
    convert "/Volumes/Project Disk/Catalyst/catalyst_icon_pack/catalyst_icon_48x48.png" -resize 32x32 "/Volumes/Project Disk/Catalyst/chrome_extension/icons/icon32.png"
else
    # If ImageMagick is not available, just copy the 48x48 icon
    cp "/Volumes/Project Disk/Catalyst/catalyst_icon_pack/catalyst_icon_48x48.png" "/Volumes/Project Disk/Catalyst/chrome_extension/icons/icon32.png"
    echo "Warning: ImageMagick not found. Using 48x48 icon as 32x32 icon without resizing."
fi

echo "Icons have been copied to the chrome_extension/icons directory."
