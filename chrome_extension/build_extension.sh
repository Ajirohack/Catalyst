#!/bin/bash

# Build script for Catalyst Chrome Extension
# This script packages the extension for distribution

echo "🛠️ Building Catalyst Chrome Extension"
echo "📅 Date: $(date)"
echo "=================================================="

# Create build directory
BUILD_DIR="./build"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Manifest version - extract from manifest.json
VERSION=$(grep -o '"version": "[^"]*"' manifest.json | cut -d'"' -f4)
echo "📦 Building version $VERSION"

# Copy required files to build directory
echo "📂 Copying files..."
cp manifest.json $BUILD_DIR/
cp background.js $BUILD_DIR/
cp content_script.js $BUILD_DIR/
cp platform_selectors.js $BUILD_DIR/
cp popup.html $BUILD_DIR/
cp popup.js $BUILD_DIR/
cp options.html $BUILD_DIR/
cp options.js $BUILD_DIR/
cp content_styles.css $BUILD_DIR/
cp login.html $BUILD_DIR/
cp login.js $BUILD_DIR/
cp welcome.html $BUILD_DIR/

# Create icons directory
mkdir -p $BUILD_DIR/icons
cp -r icons/* $BUILD_DIR/icons/

# Minify JavaScript files (if uglify-js is installed)
if command -v uglifyjs &> /dev/null; then
    echo "🔧 Minifying JavaScript files..."
    for file in $BUILD_DIR/*.js; do
        if [ -f "$file" ]; then
            uglifyjs "$file" -o "$file.min" -c -m
            mv "$file.min" "$file"
        fi
    done
else
    echo "⚠️ uglify-js not found, skipping minification"
fi

# Create zip file for Chrome Web Store
ZIP_FILE="catalyst-extension-v$VERSION.zip"
echo "📦 Creating zip file $ZIP_FILE..."
cd $BUILD_DIR
zip -r ../$ZIP_FILE *
cd ..

# Print summary
echo -e "\n✅ Build completed successfully!"
echo "📁 Build files: $BUILD_DIR/"
echo "📦 Extension package: $ZIP_FILE"
echo "📏 Package size: $(du -h $ZIP_FILE | cut -f1)"

echo -e "\n🚀 Next steps:"
echo "1. Test the extension by loading $BUILD_DIR in Chrome's developer mode"
echo "2. Upload $ZIP_FILE to the Chrome Web Store Developer Dashboard"
echo "=================================================="
