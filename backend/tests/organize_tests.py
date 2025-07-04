"""
This script organizes test files into the appropriate directories.
It moves test files based on their content and markers to the correct test category folder.
"""
import os
import re
import shutil
from pathlib import Path

# Define the root tests directory
TESTS_ROOT = Path(__file__).parent

# Define directories for different test types
UNIT_TESTS_DIR = TESTS_ROOT / "unit"
INTEGRATION_TESTS_DIR = TESTS_ROOT / "integration"
API_TESTS_DIR = TESTS_ROOT / "api"
PROPERTY_TESTS_DIR = TESTS_ROOT / "property"
PERFORMANCE_TESTS_DIR = TESTS_ROOT / "performance"
DB_TESTS_DIR = TESTS_ROOT / "db"

# Create directories if they don't exist
for directory in [UNIT_TESTS_DIR, INTEGRATION_TESTS_DIR, API_TESTS_DIR, 
                 PROPERTY_TESTS_DIR, PERFORMANCE_TESTS_DIR, DB_TESTS_DIR]:
    directory.mkdir(exist_ok=True)

# Regular expressions to identify test types
INTEGRATION_PATTERN = re.compile(r'@pytest\.mark\.integration|integration.*test|test.*integration', re.IGNORECASE)
API_PATTERN = re.compile(r'@pytest\.mark\.api|client\..*\(|TestClient|fastapi\.testclient', re.IGNORECASE)
PROPERTY_PATTERN = re.compile(r'@pytest\.mark\.property|hypothesis|given\(', re.IGNORECASE)
PERFORMANCE_PATTERN = re.compile(r'@pytest\.mark\.performance|benchmark|performance', re.IGNORECASE)
DB_PATTERN = re.compile(r'@pytest\.mark\.db|database|sqlalchemy', re.IGNORECASE)

# Files to skip (not to be moved)
SKIP_FILES = {
    "conftest.py",
    "organize_tests.py",
    "__init__.py"
}

# Special directory for tests that can't be categorized
MISC_TESTS_DIR = TESTS_ROOT / "misc"
MISC_TESTS_DIR.mkdir(exist_ok=True)

def determine_test_type(file_path):
    """Analyze file content to determine the test type."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for test type using patterns
    if INTEGRATION_PATTERN.search(content):
        return "integration"
    elif API_PATTERN.search(content):
        return "api"
    elif PROPERTY_PATTERN.search(content):
        return "property"
    elif PERFORMANCE_PATTERN.search(content):
        return "performance"
    elif DB_PATTERN.search(content):
        return "db"
    else:
        # Default to unit tests if no specific pattern is found
        return "unit"

def organize_tests():
    """Organize test files into appropriate directories."""
    test_files = [f for f in TESTS_ROOT.glob("test_*.py") if f.name not in SKIP_FILES]
    
    for file_path in test_files:
        # Skip files already in categorized directories
        if any(category in str(file_path) for category in 
               ["unit", "integration", "api", "property", "performance", "db", "misc"]):
            continue
        
        # Determine test type
        test_type = determine_test_type(file_path)
        
        # Determine target directory
        if test_type == "integration":
            target_dir = INTEGRATION_TESTS_DIR
        elif test_type == "api":
            target_dir = API_TESTS_DIR
        elif test_type == "property":
            target_dir = PROPERTY_TESTS_DIR
        elif test_type == "performance":
            target_dir = PERFORMANCE_TESTS_DIR
        elif test_type == "db":
            target_dir = DB_TESTS_DIR
        elif test_type == "unit":
            target_dir = UNIT_TESTS_DIR
        else:
            target_dir = MISC_TESTS_DIR
        
        # Move file to target directory
        target_path = target_dir / file_path.name
        
        # If target file already exists, rename with a suffix
        if target_path.exists():
            i = 1
            while (target_dir / f"{file_path.stem}_{i}{file_path.suffix}").exists():
                i += 1
            target_path = target_dir / f"{file_path.stem}_{i}{file_path.suffix}"
        
        # Copy file
        shutil.copy2(file_path, target_path)
        print(f"Moved {file_path.name} to {target_dir.name}/")
        
        # Delete original if copy successful
        if target_path.exists():
            os.remove(file_path)

def create_init_files():
    """Create __init__.py files in all test directories."""
    for directory in [TESTS_ROOT, UNIT_TESTS_DIR, INTEGRATION_TESTS_DIR, API_TESTS_DIR, 
                     PROPERTY_TESTS_DIR, PERFORMANCE_TESTS_DIR, DB_TESTS_DIR, MISC_TESTS_DIR]:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            with open(init_file, "w") as f:
                f.write("# This file is required to make Python treat this directory as a package\n")
            print(f"Created {init_file}")

if __name__ == "__main__":
    print("Organizing test files...")
    organize_tests()
    create_init_files()
    print("Test organization complete!")
