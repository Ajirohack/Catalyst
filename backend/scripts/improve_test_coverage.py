#!/usr/bin/env python3
"""Script to analyze and improve test coverage for critical services."""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple
import ast
import re


class CoverageAnalyzer:
    """Analyzes test coverage and generates improvement recommendations."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.coverage_data = {}
        self.critical_services = [
            'services/ai_service.py',
            'services/ai_service_kb.py',
            'services/knowledge_base_service.py',
            'services/project_service.py',
            'services/analysis_service.py',
            'services/enhanced_analysis_service.py',
            'routers/analysis.py',
            'routers/knowledge_base.py',
            'routers/projects.py',
            'database/models.py',
            'database/enhanced_models.py',
            'database/unified_models.py'
        ]
    
    def run_coverage_analysis(self) -> Dict:
        """Run pytest with coverage and return results."""
        try:
            # Run pytest with coverage
            cmd = [
                'pytest', 
                '--cov=.',
                '--cov-report=json:coverage.json',
                '--cov-report=term-missing',
                'tests/',
                '-q'
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.project_root, 
                capture_output=True, 
                text=True
            )
            
            # Load coverage data
            coverage_file = self.project_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    self.coverage_data = json.load(f)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'coverage_data': self.coverage_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'coverage_data': {}
            }
    
    def analyze_critical_services(self) -> Dict[str, Dict]:
        """Analyze coverage for critical services."""
        analysis = {}
        
        if not self.coverage_data or 'files' not in self.coverage_data:
            return analysis
        
        for service_path in self.critical_services:
            full_path = str(self.project_root / service_path)
            
            if full_path in self.coverage_data['files']:
                file_data = self.coverage_data['files'][full_path]
                
                analysis[service_path] = {
                    'coverage_percent': file_data['summary']['percent_covered'],
                    'missing_lines': file_data['missing_lines'],
                    'excluded_lines': file_data['excluded_lines'],
                    'total_lines': file_data['summary']['num_statements'],
                    'covered_lines': file_data['summary']['covered_lines'],
                    'needs_improvement': file_data['summary']['percent_covered'] < 60
                }
        
        return analysis
    
    def identify_uncovered_functions(self, file_path: str) -> List[Dict]:
        """Identify uncovered functions in a file."""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return []
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append({
                        'name': node.name,
                        'line_start': node.lineno,
                        'line_end': node.end_lineno or node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'is_private': node.name.startswith('_'),
                        'docstring': ast.get_docstring(node)
                    })
            
            # Check which functions are uncovered
            if file_path in self.coverage_data.get('files', {}):
                missing_lines = set(self.coverage_data['files'][str(self.project_root / file_path)]['missing_lines'])
                
                for func in functions:
                    func_lines = set(range(func['line_start'], func['line_end'] + 1))
                    func['is_uncovered'] = bool(func_lines.intersection(missing_lines))
                    func['uncovered_lines'] = list(func_lines.intersection(missing_lines))
            
            return functions
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []
    
    def generate_test_template(self, file_path: str, functions: List[Dict]) -> str:
        """Generate test template for uncovered functions."""
        module_name = file_path.replace('/', '.').replace('.py', '')
        class_name = f"Test{Path(file_path).stem.title().replace('_', '')}"
        
        template = f'"""Enhanced tests for {file_path} to improve coverage."""\n\n'
        template += 'import pytest\n'
        template += 'from unittest.mock import Mock, patch, MagicMock\n'
        template += 'from datetime import datetime, timezone\n\n'
        
        # Add specific imports based on file type
        if 'services/' in file_path:
            template += f'from {module_name} import *\n'
        elif 'routers/' in file_path:
            template += 'from fastapi.testclient import TestClient\n'
            template += f'from {module_name} import router\n'
            template += 'from main import app\n'
        elif 'database/' in file_path:
            template += 'from sqlalchemy.orm import Session\n'
            template += f'from {module_name} import *\n'
        
        template += '\n\n'
        template += f'class {class_name}:\n'
        template += '    """Test class for improved coverage."""\n\n'
        
        # Add fixtures
        if 'routers/' in file_path:
            template += '    @pytest.fixture\n'
            template += '    def client(self):\n'
            template += '        """Create test client."""\n'
            template += '        return TestClient(app)\n\n'
        
        if 'database/' in file_path:
            template += '    @pytest.fixture\n'
            template += '    def db_session(self):\n'
            template += '        """Create test database session."""\n'
            template += '        # Mock database session\n'
            template += '        return Mock()\n\n'
        
        # Generate test methods for uncovered functions
        for func in functions:
            if func.get('is_uncovered', False) and not func['name'].startswith('__'):
                test_name = f"test_{func['name']}"
                
                template += f'    def {test_name}(self):\n'
                template += f'        """Test {func["name"]} function."""\n'
                
                if func['is_async']:
                    template += '        # TODO: Implement async test\n'
                    template += '        pass\n\n'
                else:
                    template += '        # TODO: Implement test\n'
                    template += '        pass\n\n'
        
        return template
    
    def create_missing_tests(self) -> List[str]:
        """Create test files for services with low coverage."""
        analysis = self.analyze_critical_services()
        created_files = []
        
        for service_path, data in analysis.items():
            if data['needs_improvement']:
                functions = self.identify_uncovered_functions(service_path)
                uncovered_functions = [f for f in functions if f.get('is_uncovered', False)]
                
                if uncovered_functions:
                    # Generate test file
                    test_filename = f"test_{Path(service_path).stem}_coverage.py"
                    test_path = self.project_root / 'tests' / test_filename
                    
                    template = self.generate_test_template(service_path, uncovered_functions)
                    
                    with open(test_path, 'w', encoding='utf-8') as f:
                        f.write(template)
                    
                    created_files.append(str(test_path))
                    print(f"Created test file: {test_path}")
        
        return created_files
    
    def generate_coverage_report(self) -> str:
        """Generate comprehensive coverage report."""
        analysis = self.analyze_critical_services()
        
        report = "# Test Coverage Analysis Report\n\n"
        
        # Overall summary
        total_services = len(analysis)
        services_needing_improvement = sum(1 for data in analysis.values() if data['needs_improvement'])
        
        report += f"## Summary\n\n"
        report += f"- Total critical services analyzed: {total_services}\n"
        report += f"- Services needing improvement (< 60%): {services_needing_improvement}\n"
        report += f"- Services with good coverage (≥ 60%): {total_services - services_needing_improvement}\n\n"
        
        # Detailed analysis
        report += "## Detailed Analysis\n\n"
        
        for service_path, data in sorted(analysis.items(), key=lambda x: x[1]['coverage_percent']):
            status = "🔴 Needs Improvement" if data['needs_improvement'] else "✅ Good Coverage"
            
            report += f"### {service_path}\n\n"
            report += f"- **Coverage**: {data['coverage_percent']:.1f}% {status}\n"
            report += f"- **Total Lines**: {data['total_lines']}\n"
            report += f"- **Covered Lines**: {data['covered_lines']}\n"
            report += f"- **Missing Lines**: {len(data['missing_lines'])}\n"
            
            if data['missing_lines']:
                missing_ranges = self._format_line_ranges(data['missing_lines'])
                report += f"- **Missing Line Ranges**: {missing_ranges}\n"
            
            report += "\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        
        priority_services = [path for path, data in analysis.items() if data['coverage_percent'] < 40]
        if priority_services:
            report += "### High Priority (< 40% coverage)\n\n"
            for service in priority_services:
                report += f"- {service}\n"
            report += "\n"
        
        medium_services = [path for path, data in analysis.items() if 40 <= data['coverage_percent'] < 60]
        if medium_services:
            report += "### Medium Priority (40-60% coverage)\n\n"
            for service in medium_services:
                report += f"- {service}\n"
            report += "\n"
        
        report += "### Action Items\n\n"
        report += "1. **Focus on high-priority services first**\n"
        report += "2. **Add unit tests for uncovered functions**\n"
        report += "3. **Add integration tests for critical workflows**\n"
        report += "4. **Add error handling and edge case tests**\n"
        report += "5. **Mock external dependencies properly**\n"
        report += "6. **Test both success and failure scenarios**\n\n"
        
        return report
    
    def _format_line_ranges(self, lines: List[int]) -> str:
        """Format line numbers into ranges."""
        if not lines:
            return "None"
        
        lines = sorted(lines)
        ranges = []
        start = lines[0]
        end = lines[0]
        
        for line in lines[1:]:
            if line == end + 1:
                end = line
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = end = line
        
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
        
        return ", ".join(ranges)


def main():
    """Main function to improve test coverage."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    print(f"Analyzing test coverage in: {project_root}")
    
    analyzer = CoverageAnalyzer(project_root)
    
    # Run coverage analysis
    print("\n=== Running Coverage Analysis ===")
    result = analyzer.run_coverage_analysis()
    
    if not result['success']:
        print(f"Coverage analysis failed: {result['error']}")
        return
    
    # Analyze critical services
    print("\n=== Analyzing Critical Services ===")
    analysis = analyzer.analyze_critical_services()
    
    if not analysis:
        print("No coverage data found for critical services")
        return
    
    # Create missing tests
    print("\n=== Creating Missing Test Files ===")
    created_files = analyzer.create_missing_tests()
    
    # Generate report
    print("\n=== Generating Coverage Report ===")
    report = analyzer.generate_coverage_report()
    
    # Save report
    report_path = Path(project_root) / "coverage_analysis_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Coverage report saved to: {report_path}")
    print(f"Test files created: {len(created_files)}")
    
    if created_files:
        print("\nCreated test files:")
        for file_path in created_files:
            print(f"  - {file_path}")
    
    # Show summary
    services_needing_improvement = sum(1 for data in analysis.values() if data['needs_improvement'])
    print(f"\nServices needing improvement: {services_needing_improvement}/{len(analysis)}")
    
    if services_needing_improvement > 0:
        print("\n⚠️  Run the created tests and implement the TODO items to improve coverage!")
    else:
        print("\n✅ All critical services have good test coverage!")


if __name__ == "__main__":
    main()