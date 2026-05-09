"""
Code Validator Module

This module handles comprehensive code validation including syntax checking,
PEP 8 compliance, type checking, security analysis, and code quality metrics.
"""

import ast
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
import sys
from io import StringIO
import contextlib

# Third-party imports for code analysis
try:
    import black
    import autopep8
    import flake8.api.legacy as flake8
    import pylint.lint
    import mypy.api
    import bandit
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
except ImportError as e:
    print(f"Warning: Some validation dependencies not installed: {e}")


@dataclass
class ValidationResult:
    """Container for validation results."""
    is_valid: bool
    syntax_errors: List[str]
    style_issues: List[str]
    type_errors: List[str]
    security_issues: List[str]
    complexity_score: float
    maintainability_index: float
    pylint_score: float
    suggestions: List[str]
    formatted_code: Optional[str] = None


@dataclass
class CodeMetrics:
    """Container for code quality metrics."""
    lines_of_code: int
    cyclomatic_complexity: float
    maintainability_index: float
    comment_ratio: float
    function_count: int
    class_count: int


class SyntaxValidator:
    """Validates Python syntax and basic structure."""
    
    def validate(self, code: str) -> Tuple[bool, List[str]]:
        """Check if code has valid Python syntax."""
        errors = []
        
        try:
            # Parse the code using AST
            ast.parse(code)
            
            # Additional syntax checks
            self._check_indentation(code, errors)
            self._check_basic_structure(code, errors)
            
        except SyntaxError as e:
            errors.append(f"Syntax Error at line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Parsing Error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def _check_indentation(self, code: str, errors: List[str]):
        """Check for consistent indentation."""
        lines = code.split('\n')
        indent_stack = [0]
        
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue
            
            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            
            # Check if indentation is multiple of 4 (PEP 8)
            if indent % 4 != 0 and indent > 0:
                errors.append(f"Line {i}: Indentation should be multiple of 4 spaces")
    
    def _check_basic_structure(self, code: str, errors: List[str]):
        """Check basic code structure."""
        # Check for missing colons
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if (stripped.startswith(('if ', 'elif ', 'else', 'for ', 'while ', 'def ', 'class ', 'try', 'except', 'finally', 'with ')) 
                and not stripped.endswith(':') and not stripped.endswith('\\')) :
                errors.append(f"Line {i}: Missing colon at end of statement")


class StyleValidator:
    """Validates code style using PEP 8 and other standards."""
    
    def validate(self, code: str) -> Tuple[List[str], Optional[str]]:
        """Check code style and return issues and formatted code."""
        issues = []
        formatted_code = None
        
        try:
            # Use flake8 for style checking
            issues.extend(self._check_with_flake8(code))
            
            # Format code with black
            formatted_code = self._format_with_black(code)
            
            # Additional style checks
            self._check_naming_conventions(code, issues)
            self._check_line_length(code, issues)
            
        except Exception as e:
            issues.append(f"Style validation error: {str(e)}")
        
        return issues, formatted_code
    
    def _check_with_flake8(self, code: str) -> List[str]:
        """Run flake8 style checker."""
        issues = []
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                
                # Run flake8
                result = subprocess.run([
                    sys.executable, '-m', 'flake8', f.name,
                    '--select=E,W,F',  # Select error, warning, and pyflakes codes
                    '--ignore=E501'    # Ignore line length (handled separately)
                ], capture_output=True, text=True)
                
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            # Parse flake8 output
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                issues.append(f"Line {parts[1]}: {parts[3].strip()}")
                
                os.unlink(f.name)
                
        except Exception as e:
            issues.append(f"Flake8 check failed: {str(e)}")
        
        return issues
    
    def _format_with_black(self, code: str) -> str:
        """Format code using black."""
        try:
            return black.format_str(code, mode=black.FileMode())
        except Exception:
            return code
    
    def _check_naming_conventions(self, code: str, issues: List[str]):
        """Check naming conventions."""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check function names (should be snake_case)
            if stripped.startswith('def '):
                match = re.search(r'def\s+(\w+)', stripped)
                if match:
                    func_name = match.group(1)
                    if not re.match(r'^[a-z_][a-z0-9_]*$', func_name):
                        issues.append(f"Line {i}: Function '{func_name}' should use snake_case")
            
            # Check class names (should be PascalCase)
            if stripped.startswith('class '):
                match = re.search(r'class\s+(\w+)', stripped)
                if match:
                    class_name = match.group(1)
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                        issues.append(f"Line {i}: Class '{class_name}' should use PascalCase")
    
    def _check_line_length(self, code: str, issues: List[str]):
        """Check line length (PEP 8: max 79 characters)."""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                issues.append(f"Line {i}: Line too long ({len(line)} > 79 characters)")


class TypeValidator:
    """Validates type hints using mypy."""
    
    def validate(self, code: str) -> List[str]:
        """Check type hints and type consistency."""
        issues = []
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                
                # Run mypy
                result = mypy.api.run([f.name, '--ignore-missing-imports'])
                
                if result[0]:  # stdout contains errors
                    for line in result[0].strip().split('\n'):
                        if line and 'error:' in line:
                            # Parse mypy output
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                issues.append(f"Line {parts[1]}: {parts[3].strip()}")
                
                os.unlink(f.name)
                
        except Exception as e:
            issues.append(f"Type checking failed: {str(e)}")
        
        return issues


class SecurityValidator:
    """Validates code for security issues using bandit."""
    
    def validate(self, code: str) -> List[str]:
        """Check for security vulnerabilities."""
        issues = []
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                
                # Run bandit
                result = subprocess.run([
                    sys.executable, '-m', 'bandit', f.name, '-f', 'txt'
                ], capture_output=True, text=True)
                
                if result.stdout:
                    # Parse bandit output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Issue:' in line or 'Severity:' in line:
                            issues.append(line.strip())
                
                os.unlink(f.name)
                
        except Exception as e:
            issues.append(f"Security check failed: {str(e)}")
        
        return issues


class ComplexityAnalyzer:
    """Analyzes code complexity and maintainability."""
    
    def analyze(self, code: str) -> CodeMetrics:
        """Analyze code complexity and quality metrics."""
        try:
            # Calculate cyclomatic complexity
            complexity_results = cc_visit(code)
            avg_complexity = sum(result.complexity for result in complexity_results) / max(len(complexity_results), 1)
            
            # Calculate maintainability index
            mi_results = mi_visit(code, multi=True)
            avg_mi = sum(mi_results.values()) / max(len(mi_results), 1) if mi_results else 0
            
            # Basic metrics
            lines = code.split('\n')
            loc = len([line for line in lines if line.strip()])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            comment_ratio = comment_lines / max(loc, 1)
            
            # Count functions and classes
            tree = ast.parse(code)
            function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            return CodeMetrics(
                lines_of_code=loc,
                cyclomatic_complexity=avg_complexity,
                maintainability_index=avg_mi,
                comment_ratio=comment_ratio,
                function_count=function_count,
                class_count=class_count
            )
            
        except Exception as e:
            # Return default metrics if analysis fails
            return CodeMetrics(
                lines_of_code=len(code.split('\n')),
                cyclomatic_complexity=1.0,
                maintainability_index=50.0,
                comment_ratio=0.0,
                function_count=0,
                class_count=0
            )


class PylintValidator:
    """Validates code using pylint."""
    
    def validate(self, code: str) -> float:
        """Run pylint and return overall score."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                
                # Capture pylint output
                with contextlib.redirect_stdout(StringIO()) as output:
                    with contextlib.redirect_stderr(StringIO()):
                        pylint.lint.Run([f.name, '--score=y'], exit=False)
                
                # Extract score
                output_str = output.getvalue()
                score_match = re.search(r'Your code has been rated at ([\d.-]+)/10', output_str)
                score = float(score_match.group(1)) if score_match else 0.0
                
                os.unlink(f.name)
                return score
                
        except Exception:
            return 0.0


class CodeValidator:
    """Main code validator that orchestrates all validation checks."""
    
    def __init__(self):
        self.syntax_validator = SyntaxValidator()
        self.style_validator = StyleValidator()
        self.type_validator = TypeValidator()
        self.security_validator = SecurityValidator()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.pylint_validator = PylintValidator()
    
    def validate(self, code: str) -> ValidationResult:
        """Perform comprehensive code validation."""
        # Syntax validation
        syntax_valid, syntax_errors = self.syntax_validator.validate(code)
        
        # Style validation
        style_issues, formatted_code = self.style_validator.validate(code)
        
        # Type validation
        type_errors = self.type_validator.validate(code)
        
        # Security validation
        security_issues = self.security_validator.validate(code)
        
        # Complexity analysis
        metrics = self.complexity_analyzer.analyze(code)
        
        # Pylint score
        pylint_score = self.pylint_validator.validate(code)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(metrics, syntax_errors, style_issues, type_errors, security_issues)
        
        # Determine overall validity
        is_valid = (syntax_valid and 
                   len(style_issues) == 0 and 
                   len(type_errors) == 0 and 
                   len(security_issues) == 0 and
                   metrics.cyclomatic_complexity <= 10)
        
        return ValidationResult(
            is_valid=is_valid,
            syntax_errors=syntax_errors,
            style_issues=style_issues,
            type_errors=type_errors,
            security_issues=security_issues,
            complexity_score=metrics.cyclomatic_complexity,
            maintainability_index=metrics.maintainability_index,
            pylint_score=pylint_score,
            suggestions=suggestions,
            formatted_code=formatted_code
        )
    
    def _generate_suggestions(self, metrics: CodeMetrics, syntax_errors: List[str], 
                            style_issues: List[str], type_errors: List[str], 
                            security_issues: List[str]) -> List[str]:
        """Generate improvement suggestions based on validation results."""
        suggestions = []
        
        if syntax_errors:
            suggestions.append("Fix syntax errors before proceeding with other improvements")
        
        if metrics.cyclomatic_complexity > 10:
            suggestions.append("Consider breaking down complex functions into smaller ones")
        
        if metrics.maintainability_index < 20:
            suggestions.append("Code maintainability is low - consider refactoring")
        
        if metrics.comment_ratio < 0.1:
            suggestions.append("Add more comments to improve code documentation")
        
        if len(style_issues) > 5:
            suggestions.append("Consider using an auto-formatter like Black")
        
        if type_errors:
            suggestions.append("Add type hints to improve code clarity and catch errors")
        
        if security_issues:
            suggestions.append("Address security vulnerabilities before deploying")
        
        if metrics.lines_of_code > 100 and metrics.function_count == 1:
            suggestions.append("Large function detected - consider splitting into multiple functions")
        
        return suggestions
    
    def quick_fix(self, code: str) -> str:
        """Apply quick fixes to common issues."""
        # Apply autopep8 formatting
        try:
            fixed_code = autopep8.fix_code(code, options={'aggressive': 1})
            return fixed_code
        except Exception:
            return code


# Example usage
def example_usage():
    """Example usage of the CodeValidator."""
    sample_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    result = fibonacci(10)
    print(result)

if __name__ == "__main__":
    main()
    '''
    
    validator = CodeValidator()
    result = validator.validate(sample_code)
    
    print("Validation Results:")
    print(f"Is Valid: {result.is_valid}")
    print(f"Complexity Score: {result.complexity_score}")
    print(f"Maintainability Index: {result.maintainability_index}")
    print(f"Pylint Score: {result.pylint_score}")
    print(f"Syntax Errors: {result.syntax_errors}")
    print(f"Style Issues: {result.style_issues}")
    print(f"Suggestions: {result.suggestions}")


if __name__ == "__main__":
    example_usage()