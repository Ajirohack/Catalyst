#!/usr/bin/env python3
"""
Comprehensive Backend Structure and Code Analysis
Tests organization, imports, and identifies errors across the codebase
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple
import traceback

class BackendAnalyzer:
    """Analyzes backend structure and code quality"""
    
    def __init__(self, backend_path: str = "."):
        self.backend_path = Path(backend_path)
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def analyze_structure(self) -> Dict[str, any]:
        """Analyze overall backend structure"""
        print("🏗️  Analyzing Backend Structure...")
        
        structure_analysis = {
            "organization": self._check_organization(),
            "file_structure": self._analyze_file_structure(),
            "import_analysis": self._analyze_imports(),
            "code_quality": self._check_code_quality()
        }
        
        return structure_analysis
    
    def _check_organization(self) -> Dict[str, any]:
        """Check if backend follows good organization patterns"""
        print("📁 Checking organization patterns...")
        
        expected_dirs = {
            "api": "API endpoints and routing",
            "services": "Business logic services", 
            "database": "Database models and connections",
            "config": "Configuration management",
            "models": "Data models",
            "middleware": "Custom middleware",
            "validators": "Input validation",
            "schemas": "Pydantic schemas"
        }
        
        organization_score = 0
        present_dirs = {}
        
        for dir_name, description in expected_dirs.items():
            dir_path = self.backend_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                organization_score += 1
                present_dirs[dir_name] = {
                    "present": True,
                    "description": description,
                    "files": len(list(dir_path.glob("*.py")))
                }
                self.successes.append(f"✅ {dir_name}/ directory properly organized")
            else:
                present_dirs[dir_name] = {"present": False, "description": description}
                self.warnings.append(f"⚠️  Missing {dir_name}/ directory")
        
        # Check for main entry point
        main_files = ["main.py", "app.py", "server.py"]
        main_found = False
        for main_file in main_files:
            if (self.backend_path / main_file).exists():
                main_found = True
                self.successes.append(f"✅ Main entry point found: {main_file}")
                break
        
        if not main_found:
            self.issues.append("❌ No main entry point found")
        
        return {
            "score": f"{organization_score}/{len(expected_dirs)}",
            "directories": present_dirs,
            "main_entry": main_found,
            "organization_quality": "Excellent" if organization_score >= 7 else "Good" if organization_score >= 5 else "Needs Improvement"
        }
    
    def _analyze_file_structure(self) -> Dict[str, any]:
        """Analyze file structure and naming conventions"""
        print("📄 Analyzing file structure...")
        
        python_files = list(self.backend_path.rglob("*.py"))
        total_files = len(python_files)
        
        file_analysis = {
            "total_python_files": total_files,
            "by_directory": {},
            "naming_issues": [],
            "large_files": [],
            "empty_files": []
        }
        
        for py_file in python_files:
            relative_path = py_file.relative_to(self.backend_path)
            directory = relative_path.parent.name if relative_path.parent != Path('.') else "root"
            
            # Count files by directory
            if directory not in file_analysis["by_directory"]:
                file_analysis["by_directory"][directory] = 0
            file_analysis["by_directory"][directory] += 1
            
            # Check file size
            try:
                file_size = py_file.stat().st_size
                if file_size > 10000:  # Files larger than 10KB
                    file_analysis["large_files"].append(str(relative_path))
                elif file_size == 0:
                    file_analysis["empty_files"].append(str(relative_path))
            except:
                pass
            
            # Check naming conventions
            if not py_file.name.islower() or ' ' in py_file.name:
                file_analysis["naming_issues"].append(str(relative_path))
        
        return file_analysis
    
    def _analyze_imports(self) -> Dict[str, any]:
        """Analyze import statements and dependencies"""
        print("📦 Analyzing imports and dependencies...")
        
        python_files = list(self.backend_path.rglob("*.py"))
        import_analysis = {
            "total_files_checked": 0,
            "syntax_errors": [],
            "import_errors": [],
            "circular_imports": [],
            "external_dependencies": set(),
            "internal_imports": set()
        }
        
        for py_file in python_files:
            try:
                import_analysis["total_files_checked"] += 1
                
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to check syntax
                try:
                    tree = ast.parse(content)
                    
                    # Analyze imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                import_analysis["external_dependencies"].add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                module_name = node.module.split('.')[0]
                                if module_name in ['api', 'services', 'database', 'config', 'models']:
                                    import_analysis["internal_imports"].add(node.module)
                                else:
                                    import_analysis["external_dependencies"].add(module_name)
                
                except SyntaxError as e:
                    import_analysis["syntax_errors"].append(f"{py_file.relative_to(self.backend_path)}: {e}")
                    self.issues.append(f"❌ Syntax error in {py_file.relative_to(self.backend_path)}")
                
            except Exception as e:
                import_analysis["import_errors"].append(f"{py_file.relative_to(self.backend_path)}: {e}")
        
        # Convert sets to lists for JSON serialization
        import_analysis["external_dependencies"] = sorted(list(import_analysis["external_dependencies"]))
        import_analysis["internal_imports"] = sorted(list(import_analysis["internal_imports"]))
        
        return import_analysis
    
    def _check_code_quality(self) -> Dict[str, any]:
        """Check basic code quality metrics"""
        print("🔍 Checking code quality...")
        
        python_files = list(self.backend_path.rglob("*.py"))
        quality_analysis = {
            "files_with_docstrings": 0,
            "files_with_type_hints": 0,
            "files_with_tests": 0,
            "total_functions": 0,
            "total_classes": 0,
            "code_complexity": []
        }
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for docstrings
                if '"""' in content or "'''" in content:
                    quality_analysis["files_with_docstrings"] += 1
                
                # Check for type hints
                if ': ' in content and '->' in content:
                    quality_analysis["files_with_type_hints"] += 1
                
                # Parse AST for more detailed analysis
                try:
                    tree = ast.parse(content)
                    
                    functions_in_file = 0
                    classes_in_file = 0
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            functions_in_file += 1
                            quality_analysis["total_functions"] += 1
                        elif isinstance(node, ast.ClassDef):
                            classes_in_file += 1
                            quality_analysis["total_classes"] += 1
                    
                    # Calculate complexity (simple metric based on functions/classes per file)
                    complexity = functions_in_file + classes_in_file
                    if complexity > 20:
                        quality_analysis["code_complexity"].append(f"{py_file.relative_to(self.backend_path)}: {complexity} functions/classes")
                
                except SyntaxError:
                    pass  # Already captured in import analysis
                
            except Exception:
                pass
        
        return quality_analysis
    
    def test_imports(self) -> Dict[str, any]:
        """Test actual imports to find runtime errors"""
        print("🧪 Testing runtime imports...")
        
        test_results = {
            "successful_imports": [],
            "failed_imports": [],
            "missing_dependencies": []
        }
        
        # Test key modules
        key_modules = [
            "main",
            "config.settings", 
            "database.base",
            "services.enhanced_llm_router",
            "api.deps"
        ]
        
        original_path = sys.path.copy()
        sys.path.insert(0, str(self.backend_path))
        
        try:
            for module_name in key_modules:
                try:
                    spec = importlib.util.find_spec(module_name)
                    if spec is None:
                        test_results["failed_imports"].append(f"{module_name}: Module not found")
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    test_results["successful_imports"].append(module_name)
                    self.successes.append(f"✅ Successfully imported {module_name}")
                    
                except ImportError as e:
                    test_results["failed_imports"].append(f"{module_name}: {e}")
                    if "No module named" in str(e):
                        missing_dep = str(e).split("'")[1]
                        test_results["missing_dependencies"].append(missing_dep)
                    self.issues.append(f"❌ Import error in {module_name}: {e}")
                    
                except Exception as e:
                    test_results["failed_imports"].append(f"{module_name}: {e}")
                    self.issues.append(f"❌ Runtime error in {module_name}: {e}")
        
        finally:
            sys.path = original_path
        
        return test_results
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        structure_analysis = self.analyze_structure()
        import_test_results = self.test_imports()
        
        report = f"""
# 🏗️ Catalyst Backend Analysis Report

## 📊 **OVERALL ASSESSMENT**

### **Structure Quality: {structure_analysis['organization']['organization_quality']}**
- **Organization Score**: {structure_analysis['organization']['score']}
- **Total Python Files**: {structure_analysis['file_structure']['total_python_files']}
- **Successful Imports**: {len(import_test_results['successful_imports'])}
- **Failed Imports**: {len(import_test_results['failed_imports'])}

## ✅ **SUCCESSES** ({len(self.successes)})

{chr(10).join(self.successes)}

## ⚠️  **WARNINGS** ({len(self.warnings)})

{chr(10).join(self.warnings) if self.warnings else "No warnings found!"}

## ❌ **ISSUES** ({len(self.issues)})

{chr(10).join(self.issues) if self.issues else "No critical issues found!"}

## 📁 **DIRECTORY STRUCTURE**

{chr(10).join([f"- {name}: {'✅' if info['present'] else '❌'} ({info.get('files', 0)} files)" for name, info in structure_analysis['organization']['directories'].items()])}

## 📦 **DEPENDENCY ANALYSIS**

### **External Dependencies Found:**
{chr(10).join([f"- {dep}" for dep in structure_analysis['import_analysis']['external_dependencies'][:10]])}
{f"... and {len(structure_analysis['import_analysis']['external_dependencies']) - 10} more" if len(structure_analysis['import_analysis']['external_dependencies']) > 10 else ""}

### **Internal Module Structure:**
{chr(10).join([f"- {module}" for module in structure_analysis['import_analysis']['internal_imports'][:10]])}

## 🧪 **IMPORT TEST RESULTS**

### **Successful Imports:**
{chr(10).join([f"✅ {module}" for module in import_test_results['successful_imports']])}

### **Failed Imports:**
{chr(10).join([f"❌ {error}" for error in import_test_results['failed_imports']])}

## 📈 **CODE QUALITY METRICS**

- **Files with Docstrings**: {structure_analysis['code_quality']['files_with_docstrings']}
- **Files with Type Hints**: {structure_analysis['code_quality']['files_with_type_hints']}
- **Total Functions**: {structure_analysis['code_quality']['total_functions']}
- **Total Classes**: {structure_analysis['code_quality']['total_classes']}

## 🎯 **RECOMMENDATIONS**

### **HIGH PRIORITY:**
{chr(10).join([f"- Fix: {issue.replace('❌ ', '')}" for issue in self.issues[:5]])}

### **MEDIUM PRIORITY:**
{chr(10).join([f"- Address: {warning.replace('⚠️  ', '')}" for warning in self.warnings[:5]])}

## 🏆 **FINAL VERDICT**

**Backend Organization**: {'✅ Excellent' if len(self.issues) == 0 else '⚠️ Good with minor issues' if len(self.issues) < 5 else '❌ Needs attention'}
**Code Quality**: {'✅ High' if structure_analysis['code_quality']['files_with_docstrings'] > 10 else '⚠️ Medium' if structure_analysis['code_quality']['files_with_docstrings'] > 5 else '❌ Low'}
**Ready for Production**: {'✅ Yes' if len(self.issues) == 0 else '⚠️ With fixes' if len(self.issues) < 3 else '❌ Needs work'}
"""
        
        return report

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Backend Analysis...")
    print("=" * 60)
    
    analyzer = BackendAnalyzer()
    report = analyzer.generate_report()
    
    print(report)
    
    # Save report to file
    with open("BACKEND_ANALYSIS_REPORT.md", "w") as f:
        f.write(report)
    
    print("\n📝 Report saved to BACKEND_ANALYSIS_REPORT.md")
    print(f"\n🎯 Analysis complete! Found {len(analyzer.issues)} issues, {len(analyzer.warnings)} warnings, {len(analyzer.successes)} successes")
