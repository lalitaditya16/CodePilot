"""Tests for CodeGenerator module."""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from code_generator import CodeGenerator, CodeGenerationRequest, GeneratedCode


class TestCodeGenerator(unittest.TestCase):
    """Test cases for CodeGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_openai_response = Mock()
        self.mock_openai_response.choices = [Mock()]
        self.mock_openai_response.choices[0].message.content = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
    
    @patch('code_generator.openai.OpenAI')
    def test_simple_code_generation(self, mock_openai):
        """Test simple code generation."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = self.mock_openai_response
        mock_openai.return_value = mock_client
        
        # Test with mock API key
        with patch('config.settings.settings.OPENAI_API_KEY', 'test-key'):
            generator = CodeGenerator('openai')
            result = generator.generate_simple("Create a fibonacci function")
            
            self.assertIsInstance(result, str)
            self.assertIn('fibonacci', result.lower())
            self.assertIn('def', result)
    
    def test_code_generation_request(self):
        """Test CodeGenerationRequest creation."""
        request = CodeGenerationRequest(
            description="Test function",
            function_name="test_func",
            parameters=["x: int", "y: str"],
            return_type="bool"
        )
        
        self.assertEqual(request.description, "Test function")
        self.assertEqual(request.function_name, "test_func")
        self.assertEqual(len(request.parameters), 2)
        self.assertEqual(request.return_type, "bool")
    
    def test_code_cleaning(self):
        """Test code cleaning functionality."""
        generator = CodeGenerator.__new__(CodeGenerator)  # Create without __init__
        
        dirty_code = '''```python
def test():
    print("hello")
```'''
        
        clean_code = generator._clean_code(dirty_code)
        
        self.assertNotIn('```', clean_code)
        self.assertIn('def test():', clean_code)
    
    def test_function_name_extraction(self):
        """Test function name extraction."""
        generator = CodeGenerator.__new__(CodeGenerator)  # Create without __init__
        
        code = '''
def my_function(x, y):
    return x + y
'''
        
        function_name = generator._extract_function_name(code)
        self.assertEqual(function_name, 'my_function')
    
    def test_dependency_extraction(self):
        """Test dependency extraction."""
        generator = CodeGenerator.__new__(CodeGenerator)  # Create without __init__
        
        code = '''
import os
import sys
from math import sqrt
import numpy as np
'''
        
        dependencies = generator._extract_dependencies(code)
        expected_deps = ['os', 'sys', 'math', 'numpy']
        
        for dep in expected_deps:
            self.assertIn(dep, dependencies)
    
    def test_complexity_estimation(self):
        """Test complexity estimation."""
        generator = CodeGenerator.__new__(CodeGenerator)  # Create without __init__
        
        simple_code = '''
def simple():
    return 42
'''
        
        complex_code = '''
def complex(n):
    if n > 0:
        for i in range(n):
            if i % 2 == 0:
                while i > 0:
                    try:
                        i -= 1
                    except:
                        break
    return n
'''
        
        simple_complexity = generator._estimate_complexity(simple_code)
        complex_complexity = generator._estimate_complexity(complex_code)
        
        self.assertLess(simple_complexity, complex_complexity)
    
    def test_potential_issues_detection(self):
        """Test potential issues detection."""
        generator = CodeGenerator.__new__(CodeGenerator)  # Create without __init__
        
        risky_code = '''
import os
def risky_function():
    eval("print('hello')")
    os.system("ls")
'''
        
        warnings = generator._check_potential_issues(risky_code)
        
        self.assertTrue(len(warnings) > 0)
        self.assertTrue(any('eval' in warning or 'unsafe' in warning.lower() for warning in warnings))


if __name__ == '__main__':
    unittest.main()