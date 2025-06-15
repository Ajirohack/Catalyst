#!/bin/bash

# Script to update GitHub repository with necessary files for Catalyst project
# Created on June 15, 2025

echo "🚀 Starting GitHub repository update for Catalyst..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ] || [ ! -d "chrome_extension" ]; then
    echo "❌ Please run this script from the root of the Catalyst project."
    exit 1
fi

# Configure Git if needed
if [ -z "$(git config --get user.name)" ]; then
    echo "Enter your GitHub username:"
    read username
    git config user.name "$username"
fi

if [ -z "$(git config --get user.email)" ]; then
    echo "Enter your GitHub email:"
    read email
    git config user.email "$email"
fi

# Initialize git repository if it doesn't exist
if [ ! -d .git ]; then
    echo "Initializing Git repository..."
    git init
    echo "Adding remote repository..."
    git remote add origin https://github.com/Ajirohack/Catalyst.git
else
    # Check if remote exists, if not add it
    if ! git remote | grep -q "origin"; then
        echo "Adding remote repository..."
        git remote add origin https://github.com/Ajirohack/Catalyst.git
    fi
fi

# Create .gitignore file to exclude unnecessary files
echo "Creating .gitignore file..."
cat > .gitignore << EOL
# Logs
logs/
*.log

# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Node modules
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# VS Code
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# macOS
.DS_Store
.AppleDouble
.LSOverride
._*

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Test data
test_results/
EOL

# Check if there are any existing changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "There are uncommitted changes. Would you like to commit them? (y/n)"
    read answer
    if [ "$answer" = "y" ]; then
        git add -A
        echo "Enter commit message for existing changes:"
        read message
        git commit -m "$message"
    fi
fi

# Stage necessary files and folders
echo "Staging necessary files and folders..."

# Add main project files
git add README.md
git add docker-compose.yml
git add DOCKER.md
git add package.json
git add wire-admin.md
git add wire-user.md
git add .gitignore

# Add backend files (selectively)
git add backend/Dockerfile
git add backend/main.py
git add backend/README.md
git add backend/requirements.txt
git add backend/config/*.py
git add backend/database/*.py
git add backend/docs/*.py
git add backend/middleware/*.py
git add backend/models/*.py
git add backend/routers/*.py
git add backend/schemas/*.py
git add backend/services/*.py
git add backend/tests/*.py
git add backend/tests/*.sh
git add backend/validators/*.py

# Add frontend files (selectively)
git add frontend/package.json
git add frontend/postcss.config.js
git add frontend/tailwind.config.js
git add frontend/public/*
git add frontend/src/*.jsx
git add frontend/src/*.css
git add frontend/src/components/*
git add frontend/src/context/*
git add frontend/src/layout/*
git add frontend/src/lib/*
git add frontend/src/pages/*

# Add chrome extension files
git add chrome_extension/*.js
git add chrome_extension/*.html
git add chrome_extension/*.css
git add chrome_extension/*.json
git add chrome_extension/*.sh
git add chrome_extension/*.md
git add chrome_extension/icons/*
git add chrome_extension/testing/*.js
git add chrome_extension/testing/*.html
git add chrome_extension/testing/*.md
git add chrome_extension/testing/platforms/*
git add chrome_extension/testing/uat/*

# Add icon pack
git add catalyst_icon_pack/*

# Check if we have something to commit
if git diff --cached --quiet; then
    echo "No changes to commit."
else
    # Commit the changes
    echo "Committing changes..."
    git commit -m "Update repository with necessary project files - $(date)"

    # Push to GitHub
    echo "Pushing to GitHub..."
    git push -u origin main || git push -u origin master

    echo "✅ Successfully updated GitHub repository with necessary files!"
fi
