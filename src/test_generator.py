"""
Test Generator Module

This module handles automatic test case generation and execution for Python code.
It can generate unit tests, integration tests, and property-based tests.
"""

import ast
import inspect
import re
import subprocess
import tempfile
import os
import sys
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
import json
import importlib.util
from io import StringIO
import contextlib

# Test framework imports
try:
    import pytest
    import hypothesis
    from hypothesis import strategies as st
except ImportError as e:
    print(f"Warning: Some testing dependencies not installed: {e}")

from config.settings import settings


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    description: str
    inputs: Dict[str, Any]
    expected_output: Any
    test_type: str  # 'unit', 'integration', 'property'
    assertions: List[str]


@dataclass
class TestSuite:
    """Collection of test cases for a function or class."""
    target_function: str
    test_cases: List[TestCase]
    setup_code: str
    teardown_code: str


@dataclass
class TestExecutionResult:
    """Results from test execution."""
    passed: int
    failed: int
    skipped: int
    total: int
    coverage_percentage: float
    failures: List[str]
    execution_time: float
    detailed_results: List[Dict[str, Any]]


class CodeAnalyzer:
    """Analyzes code to extract function signatures and types."""
    
    def analyze_function(self, code: str, function_name: str) -> Dict[str, Any]:
        """Analyze a function to extract its signature and docstring."""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    return {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'defaults': [ast.unparse(default) if hasattr(ast, 'unparse') else str(default) 
                                   for default in node.args.defaults],
                        'return_annotation': ast.unparse(node.returns) if node.returns else None,
                        'docstring': ast.get_docstring(node),
                        'arg_annotations': {arg.arg: ast.unparse(arg.annotation) if arg.annotation else None 
                                          for arg in node.args.args}
                    }
            
            return {}
        except Exception as e:
            print(f"Error analyzing function: {e}")
            return {}
    
    def extract_all_functions(self, code: str) -> List[str]:
        """Extract all function names from code."""
        try:
            tree = ast.parse(code)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except Exception:
            return []


class TestCaseGenerator:
    """Generates test cases for Python functions."""
    
    def __init__(self):
        self.analyzer = CodeAnalyzer()
    
    def generate_unit_tests(self, code: str, function_name: str) -> List[TestCase]:
        """Generate unit tests for a specific function."""
        func_info = self.analyzer.analyze_function(code, function_name)
        if not func_info:
            return []
        
        test_cases = []
        
        # Generate basic test cases
        test_cases.extend(self._generate_basic_tests(func_info))
        
        # Generate edge case tests
        test_cases.extend(self._generate_edge_case_tests(func_info))
        
        # Generate error case tests
        test_cases.extend(self._generate_error_case_tests(func_info))
        
        return test_cases
    
    def _generate_basic_tests(self, func_info: Dict[str, Any]) -> List[TestCase]:
        """Generate basic happy path test cases."""
        test_cases = []
        func_name = func_info['name']
        args = func_info['args']
        
        # Generate tests based on function name patterns
        if 'factorial' in func_name.lower():
            test_cases.append(TestCase(
                name=f"test_{func_name}_basic",
                description="Test factorial with positive integer",
                inputs={'n': 5},
                expected_output=120,
                test_type='unit',
                assertions=[f"assert {func_name}(5) == 120"]
            ))
        
        elif 'fibonacci' in func_name.lower():
            test_cases.append(TestCase(
                name=f"test_{func_name}_basic",
                description="Test fibonacci sequence",
                inputs={'n': 7},
                expected_output=13,
                test_type='unit',
                assertions=[f"assert {func_name}(7) == 13"]
            ))
        
        elif 'sort' in func_name.lower():
            test_cases.append(TestCase(
                name=f"test_{func_name}_basic",
                description="Test sorting functionality",
                inputs={'arr': [3, 1, 4, 1, 5]},
                expected_output=[1, 1, 3, 4, 5],
                test_type='unit',
                assertions=[f"assert {func_name}([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]"]
            ))
        
        elif 'search' in func_name.lower():
            test_cases.append(TestCase(
                name=f"test_{func_name}_found",
                description="Test search when item is found",
                inputs={'arr': [1, 2, 3, 4, 5], 'target': 3},
                expected_output=2,
                test_type='unit',
                assertions=[f"assert {func_name}([1, 2, 3, 4, 5], 3) == 2"]
            ))
        
        else:
            # Generic test case
            test_cases.append(TestCase(
                name=f"test_{func_name}_basic",
                description=f"Basic test for {func_name}",
                inputs={arg: self._generate_sample_input(arg) for arg in args},
                expected_output=None,  # Will be determined by execution
                test_type='unit',
                assertions=[f"result = {func_name}({', '.join(args)})", "assert result is not None"]
            ))
        
        return test_cases
    
    def _generate_edge_case_tests(self, func_info: Dict[str, Any]) -> List[TestCase]:
        """Generate edge case test cases."""
        test_cases = []
        func_name = func_info['name']
        args = func_info['args']
        
        # Common edge cases based on function patterns
        if any(arg in func_name.lower() for arg in ['factorial', 'fibonacci', 'power']):
            # Test with 0
            test_cases.append(TestCase(
                name=f"test_{func_name}_zero",
                description="Test with zero input",
                inputs={'n': 0},
                expected_output=None,
                test_type='unit',
                assertions=[f"result = {func_name}(0)", "assert result is not None"]
            ))
            
            # Test with 1
            test_cases.append(TestCase(
                name=f"test_{func_name}_one",
                description="Test with one",
                inputs={'n': 1},
                expected_output=None,
                test_type='unit',
                assertions=[f"result = {func_name}(1)", "assert result is not None"]
            ))
        
        if 'list' in str(func_info.get('arg_annotations', {})).lower() or 'arr' in args:
            # Test with empty list
            test_cases.append(TestCase(
                name=f"test_{func_name}_empty_list",
                description="Test with empty list",
                inputs={'arr': []},
                expected_output=None,
                test_type='unit',
                assertions=[f"result = {func_name}([])", "assert result is not None"]
            ))
            
            # Test with single element
            test_cases.append(TestCase(
                name=f"test_{func_name}_single_element",
                description="Test with single element list",
                inputs={'arr': [42]},
                expected_output=None,
                test_type='unit',
                assertions=[f"result = {func_name}([42])", "assert result is not None"]
            ))
        
        return test_cases
    
    def _generate_error_case_tests(self, func_info: Dict[str, Any]) -> List[TestCase]:
        """Generate test cases for error conditions."""
        test_cases = []
        func_name = func_info['name']
        args = func_info['args']
        
        # Test with negative numbers where inappropriate
        if any(arg in func_name.lower() for arg in ['factorial', 'sqrt', 'log']):
            test_cases.append(TestCase(
                name=f"test_{func_name}_negative",
                description="Test with negative input",
                inputs={'n': -1},
                expected_output="ValueError",
                test_type='unit',
                assertions=[
                    "import pytest",
                    f"with pytest.raises(ValueError):",
                    f"    {func_name}(-1)"
                ]
            ))
        
        # Test with None inputs
        if len(args) > 0:
            test_cases.append(TestCase(
                name=f"test_{func_name}_none_input",
                description="Test with None input",
                inputs={args[0]: None},
                expected_output="TypeError",
                test_type='unit',
                assertions=[
                    "import pytest",
                    f"with pytest.raises((TypeError, AttributeError)):",
                    f"    {func_name}(None)"
                ]
            ))
        
        return test_cases
    
    def _generate_sample_input(self, arg_name: str) -> Any:
        """Generate sample input based on argument name."""
        if 'n' in arg_name.lower() or 'num' in arg_name.lower() or 'count' in arg_name.lower():
            return 5
        elif 'arr' in arg_name.lower() or 'list' in arg_name.lower():
            return [1, 2, 3, 4, 5]
        elif 'str' in arg_name.lower() or 'text' in arg_name.lower():
            return "sample"
        elif 'target' in arg_name.lower():
            return 3
        else:
            return "test_value"


class PropertyBasedTestGenerator:
    """Generates property-based tests using Hypothesis."""
    
    def generate_property_tests(self, code: str, function_name: str) -> List[TestCase]:
        """Generate property-based tests for a function."""
        test_cases = []
        
        # Analyze function to determine appropriate strategies
        func_info = CodeAnalyzer().analyze_function(code, function_name)
        if not func_info:
            return test_cases
        
        # Generate property tests based on function characteristics
        if 'sort' in function_name.lower():
            test_cases.append(self._generate_sort_property_test(function_name))
        elif 'reverse' in function_name.lower():
            test_cases.append(self._generate_reverse_property_test(function_name))
        elif any(op in function_name.lower() for op in ['add', 'sum', 'multiply']):
            test_cases.append(self._generate_arithmetic_property_test(function_name))
        
        return test_cases
    
    def _generate_sort_property_test(self, func_name: str) -> TestCase:
        """Generate property test for sorting functions."""
        return TestCase(
            name=f"test_{func_name}_property_sorted",
            description="Property test: result should be sorted",
            inputs={},
            expected_output=None,
            test_type='property',
            assertions=[
                "from hypothesis import given, strategies as st",
                "@given(st.lists(st.integers()))",
                f"def test_{func_name}_is_sorted(lst):",
                f"    result = {func_name}(lst)",
                "    assert result == sorted(result)"
            ]
        )
    
    def _generate_reverse_property_test(self, func_name: str) -> TestCase:
        """Generate property test for reverse functions."""
        return TestCase(
            name=f"test_{func_name}_property_double_reverse",
            description="Property test: double reverse equals original",
            inputs={},
            expected_output=None,
            test_type='property',
            assertions=[
                "from hypothesis import given, strategies as st",
                "@given(st.lists(st.integers()))",
                f"def test_{func_name}_double_reverse(lst):",
                f"    result = {func_name}({func_name}(lst))",
                "    assert result == lst"
            ]
        )
    
    def _generate_arithmetic_property_test(self, func_name: str) -> TestCase:
        """Generate property test for arithmetic functions."""
        return TestCase(
            name=f"test_{func_name}_property_commutative",
            description="Property test: operation should be commutative",
            inputs={},
            expected_output=None,
            test_type='property',
            assertions=[
                "from hypothesis import given, strategies as st",
                "@given(st.integers(), st.integers())",
                f"def test_{func_name}_commutative(a, b):",
                f"    assert {func_name}(a, b) == {func_name}(b, a)"
            ]
        )


class TestExecutor:
    """Executes generated test cases and collects results."""
    
    def execute_tests(self, code: str, test_suite: TestSuite) -> TestExecutionResult:
        """Execute test suite and return results."""
        # Create temporary test file
        test_code = self._generate_test_file(code, test_suite)
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_code)
                f.flush()
                
                # Run pytest
                result = subprocess.run([
                    sys.executable, '-m', 'pytest', f.name, '-v', '--tb=short'
                ], capture_output=True, text=True, timeout=30)
                
                # Parse results
                execution_result = self._parse_pytest_output(result.stdout, result.stderr)
                
                os.unlink(f.name)
                return execution_result
                
        except Exception as e:
            return TestExecutionResult(
                passed=0, failed=1, skipped=0, total=1,
                coverage_percentage=0.0, failures=[str(e)],
                execution_time=0.0, detailed_results=[]
            )
    
    def _generate_test_file(self, code: str, test_suite: TestSuite) -> str:
        """Generate complete test file."""
        test_file_parts = [
            "import pytest",
            "import sys",
            "from typing import *",
            "",
            "# Original code under test",
            code,
            "",
            "# Test cases"
        ]
        
        if test_suite.setup_code:
            test_file_parts.extend(["# Setup", test_suite.setup_code, ""])
        
        for test_case in test_suite.test_cases:
            test_file_parts.extend([
                f"def {test_case.name}():",
                f'    """{test_case.description}"""'
            ])
            
            for assertion in test_case.assertions:
                test_file_parts.append(f"    {assertion}")
            
            test_file_parts.append("")
        
        if test_suite.teardown_code:
            test_file_parts.extend(["# Teardown", test_suite.teardown_code])
        
        return "\n".join(test_file_parts)
    
    def _parse_pytest_output(self, stdout: str, stderr: str) -> TestExecutionResult:
        """Parse pytest output to extract results."""
        passed = failed = skipped = 0
        failures = []
        execution_time = 0.0
        
        # Parse test results
        lines = stdout.split('\n')
        
        for line in lines:
            if ' passed' in line:
                match = re.search(r'(\d+) passed', line)
                if match:
                    passed = int(match.group(1))
            
            if ' failed' in line:
                match = re.search(r'(\d+) failed', line)
                if match:
                    failed = int(match.group(1))
            
            if ' skipped' in line:
                match = re.search(r'(\d+) skipped', line)
                if match:
                    skipped = int(match.group(1))
            
            if 'FAILED' in line:
                failures.append(line.strip())
            
            if 'seconds' in line:
                match = re.search(r'([\d.]+) seconds', line)
                if match:
                    execution_time = float(match.group(1))
        
        total = passed + failed + skipped
        
        return TestExecutionResult(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            coverage_percentage=0.0,  # Would need coverage.py integration
            failures=failures,
            execution_time=execution_time,
            detailed_results=[]
        )


class TestGenerator:
    """Main test generator class that orchestrates test generation and execution."""
    
    def __init__(self):
        self.test_case_generator = TestCaseGenerator()
        self.property_test_generator = PropertyBasedTestGenerator()
        self.executor = TestExecutor()
    
    def generate_and_run_tests(self, code: str, function_name: str = None) -> Dict[str, Any]:
        """Generate and execute tests for given code."""
        results = {}
        
        # Extract function names if not specified
        if function_name is None:
            functions = CodeAnalyzer().extract_all_functions(code)
        else:
            functions = [function_name]
        
        for func in functions:
            # Generate unit tests
            unit_tests = self.test_case_generator.generate_unit_tests(code, func)
            
            # Generate property tests
            property_tests = self.property_test_generator.generate_property_tests(code, func)
            
            # Create test suite
            test_suite = TestSuite(
                target_function=func,
                test_cases=unit_tests + property_tests,
                setup_code="",
                teardown_code=""
            )
            
            # Execute tests
            execution_result = self.executor.execute_tests(code, test_suite)
            
            results[func] = {
                'test_suite': test_suite,
                'execution_result': execution_result,
                'test_count': len(test_suite.test_cases)
            }
        
        return results
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report."""
        report_lines = [
            "# Test Execution Report",
            "=" * 50,
            ""
        ]
        
        total_passed = total_failed = total_tests = 0
        
        for func_name, result in results.items():
            exec_result = result['execution_result']
            total_passed += exec_result.passed
            total_failed += exec_result.failed
            total_tests += exec_result.total
            
            report_lines.extend([
                f"## Function: {func_name}",
                f"- Tests Generated: {result['test_count']}",
                f"- Tests Passed: {exec_result.passed}",
                f"- Tests Failed: {exec_result.failed}",
                f"- Execution Time: {exec_result.execution_time:.2f}s",
                ""
            ])
            
            if exec_result.failures:
                report_lines.extend([
                    "### Failures:",
                    *[f"- {failure}" for failure in exec_result.failures],
                    ""
                ])
        
        # Summary
        success_rate = (total_passed / max(total_tests, 1)) * 100
        report_lines.extend([
            "## Summary",
            f"- Total Tests: {total_tests}",
            f"- Passed: {total_passed}",
            f"- Failed: {total_failed}",
            f"- Success Rate: {success_rate:.1f}%"
        ])
        
        return "\n".join(report_lines)


# Example usage
def example_usage():
    """Example usage of the TestGenerator."""
    sample_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    """Calculate the factorial of n."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n-1)
    '''
    
    generator = TestGenerator()
    results = generator.generate_and_run_tests(sample_code)
    
    print("Test Generation Results:")
    for func_name, result in results.items():
        print(f"\nFunction: {func_name}")
        print(f"Tests generated: {result['test_count']}")
        exec_result = result['execution_result']
        print(f"Passed: {exec_result.passed}, Failed: {exec_result.failed}")
    
    print("\n" + "="*50)
    print(generator.generate_test_report(results))


if __name__ == "__main__":
    example_usage()