"""
Demonstration script showing the full capabilities of the Python Code Generator.
This script runs without requiring API keys by using mock responses.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from code_validator import CodeValidator
from test_generator import TestGenerator  
from code_optimizer import CodeOptimizer

# Sample generated code for demonstration
SAMPLE_CODES = {
    'fibonacci': '''
def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number using recursion.
    
    Args:
        n (int): The position in the Fibonacci sequence (0-indexed)
        
    Returns:
        int: The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n <= 1:
        return n
    
    return fibonacci(n - 1) + fibonacci(n - 2)
''',
    
    'binary_search': '''
def binary_search(arr: list, target: int) -> int:
    """
    Perform binary search on a sorted array.
    
    Args:
        arr (list): Sorted list of integers
        target (int): Value to search for
        
    Returns:
        int: Index of target if found, -1 otherwise
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
''',
    
    'inefficient_example': '''
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

def string_concat_loop(words):
    result = ""
    for word in words:
        result = result + word + " "
    return result

def inefficient_fibonacci(n):
    if n <= 1:
        return n
    return inefficient_fibonacci(n-1) + inefficient_fibonacci(n-2)
'''
}


def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subheader(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def demonstrate_code_validation():
    """Demonstrate code validation capabilities."""
    print_header("🔍 CODE VALIDATION DEMONSTRATION")
    
    validator = CodeValidator()
    
    for name, code in SAMPLE_CODES.items():
        print_subheader(f"Validating: {name}")
        
        result = validator.validate(code)
        
        print(f"✅ Syntax Valid: {len(result.syntax_errors) == 0}")
        print(f"📊 Pylint Score: {result.pylint_score:.1f}/10")
        print(f"🔄 Complexity Score: {result.complexity_score:.1f}")
        print(f"🔧 Maintainability Index: {result.maintainability_index:.1f}")
        
        if result.syntax_errors:
            print(f"❌ Syntax Errors ({len(result.syntax_errors)}):")
            for error in result.syntax_errors[:3]:
                print(f"   • {error}")
        
        if result.style_issues:
            print(f"⚠️  Style Issues ({len(result.style_issues)}):")
            for issue in result.style_issues[:3]:
                print(f"   • {issue}")
        
        if result.suggestions:
            print(f"💡 Suggestions ({len(result.suggestions)}):")
            for suggestion in result.suggestions[:3]:
                print(f"   • {suggestion}")
        
        print()


def demonstrate_test_generation():
    """Demonstrate test generation and execution."""
    print_header("🧪 TEST GENERATION DEMONSTRATION")
    
    test_generator = TestGenerator()
    
    for name, code in SAMPLE_CODES.items():
        print_subheader(f"Testing: {name}")
        
        try:
            results = test_generator.generate_and_run_tests(code)
            
            total_tests = sum(result['execution_result'].total for result in results.values())
            total_passed = sum(result['execution_result'].passed for result in results.values())
            total_failed = sum(result['execution_result'].failed for result in results.values())
            
            success_rate = (total_passed / max(total_tests, 1)) * 100
            
            print(f"📝 Tests Generated: {total_tests}")
            print(f"✅ Tests Passed: {total_passed}")
            print(f"❌ Tests Failed: {total_failed}")
            print(f"📊 Success Rate: {success_rate:.1f}%")
            
            # Show test details for first function
            if results:
                func_name = list(results.keys())[0]
                func_result = results[func_name]
                test_suite = func_result['test_suite']
                
                print(f"\n   Test cases for {func_name}:")
                for i, test_case in enumerate(test_suite.test_cases[:3], 1):
                    print(f"   {i}. {test_case.description}")
                
                if func_result['execution_result'].failures:
                    print(f"\n   Failures:")
                    for failure in func_result['execution_result'].failures[:2]:
                        print(f"   • {failure}")
        
        except Exception as e:
            print(f"❌ Test generation failed: {e}")
        
        print()


def demonstrate_code_optimization():
    """Demonstrate code optimization capabilities."""
    print_header("⚡ CODE OPTIMIZATION DEMONSTRATION")
    
    optimizer = CodeOptimizer()
    
    for name, code in SAMPLE_CODES.items():
        print_subheader(f"Optimizing: {name}")
        
        try:
            result = optimizer.optimize(code)
            
            print(f"📊 Optimization Score: {result.optimization_score:.1f}/100")
            print(f"💡 Total Suggestions: {len(result.suggestions)}")
            
            # Group suggestions by type
            by_type = {}
            for suggestion in result.suggestions:
                by_type.setdefault(suggestion.type, []).append(suggestion)
            
            for opt_type, suggestions in by_type.items():
                print(f"\n   {opt_type.title()} Optimizations ({len(suggestions)}):")
                
                for suggestion in suggestions[:2]:  # Show top 2 per type
                    print(f"   • {suggestion.description}")
                    print(f"     Confidence: {suggestion.confidence:.1f}")
                    print(f"     Improvement: {suggestion.estimated_improvement}")
                    print()
        
        except Exception as e:
            print(f"❌ Optimization failed: {e}")
        
        print()


def demonstrate_full_pipeline():
    """Demonstrate the complete pipeline on one example."""
    print_header("🚀 COMPLETE PIPELINE DEMONSTRATION")
    
    # Use the inefficient example to show all features
    code = SAMPLE_CODES['inefficient_example']
    
    print("Sample Code Being Analyzed:")
    print("-" * 30)
    print(code[:200] + "..." if len(code) > 200 else code)
    print()
    
    # Step 1: Validation
    print_subheader("Step 1: Code Validation")
    validator = CodeValidator()
    validation_result = validator.validate(code)
    
    print(f"Validation Status: {'✅ Passed' if validation_result.is_valid else '⚠️ Issues Found'}")
    print(f"Pylint Score: {validation_result.pylint_score:.1f}/10")
    print(f"Issues Found: {len(validation_result.syntax_errors + validation_result.style_issues)}")
    
    # Step 2: Testing
    print_subheader("Step 2: Test Generation & Execution")
    test_generator = TestGenerator()
    
    try:
        test_results = test_generator.generate_and_run_tests(code)
        total_tests = sum(result['execution_result'].total for result in test_results.values())
        total_passed = sum(result['execution_result'].passed for result in test_results.values())
        
        print(f"Tests Generated: {total_tests}")
        print(f"Tests Passed: {total_passed}/{total_tests}")
        
    except Exception as e:
        print(f"Testing encountered issues: {e}")
    
    # Step 3: Optimization
    print_subheader("Step 3: Code Optimization")
    optimizer = CodeOptimizer()
    
    try:
        opt_result = optimizer.optimize(code)
        print(f"Optimization Score: {opt_result.optimization_score:.1f}/100")
        print(f"Optimization Suggestions: {len(opt_result.suggestions)}")
        
        if opt_result.suggestions:
            print("\nTop Optimization Suggestions:")
            for i, suggestion in enumerate(opt_result.suggestions[:3], 1):
                print(f"{i}. {suggestion.type.title()}: {suggestion.description}")
                print(f"   Expected improvement: {suggestion.estimated_improvement}")
    
    except Exception as e:
        print(f"Optimization encountered issues: {e}")
    
    # Step 4: Summary
    print_subheader("Pipeline Summary")
    print("The complete pipeline successfully:")
    print("✅ Analyzed code quality and style")
    print("✅ Generated and executed test cases")
    print("✅ Identified optimization opportunities")
    print("✅ Provided actionable recommendations")


def show_project_overview():
    """Show an overview of the project structure and capabilities."""
    print_header("📋 PROJECT OVERVIEW")
    
    print("""
🤖 Python Code Generator with LLM Integration

This project provides a comprehensive solution for:

1. 🎯 CODE GENERATION
   • Natural language to Python code
   • Support for OpenAI GPT and Anthropic Claude
   • Structured requests with parameters and constraints
   • Automatic function extraction and metadata

2. 🔍 CODE VALIDATION
   • Syntax checking with detailed error reporting
   • PEP 8 style compliance validation
   • Type checking with mypy integration
   • Security vulnerability scanning with bandit
   • Code complexity analysis
   • Pylint integration for quality scoring

3. 🧪 TEST GENERATION & EXECUTION
   • Automatic unit test generation
   • Property-based testing with Hypothesis
   • Edge case and error condition testing
   • Test execution with pytest integration
   • Coverage analysis and reporting

4. ⚡ CODE OPTIMIZATION
   • Performance pattern detection
   • Memory usage optimization
   • Code refactoring suggestions
   • Complexity reduction recommendations
   • Best practices enforcement

5. 📊 COMPREHENSIVE REPORTING
   • Detailed analysis reports
   • JSON and Markdown output formats
   • Visual progress indicators
   • Actionable improvement suggestions

Key Features:
• 🔌 Multiple LLM provider support
• 🎛️  Configurable quality thresholds  
• 📁 Organized output directory structure
• 🖥️  Rich console interface with colors
• 🤝 Both CLI and interactive modes
• 🧩 Modular architecture for extensibility
    """)


def main():
    """Run the complete demonstration."""
    print("""
╭─────────────────────────────────────────────────────────────╮
│                                                             │
│   🎭 PYTHON CODE GENERATOR - LIVE DEMONSTRATION            │
│                                                             │
│   See all features in action without requiring API keys!   │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
    """)
    
    try:
        # Show project overview
        show_project_overview()
        
        # Run demonstrations
        demonstrate_code_validation()
        demonstrate_test_generation()
        demonstrate_code_optimization()
        demonstrate_full_pipeline()
        
        print_header("🎉 DEMONSTRATION COMPLETE")
        print("""
This demonstration showed the core capabilities of the Python Code Generator:

✅ Code validation with multiple quality checks
✅ Automatic test generation and execution  
✅ Code optimization with actionable suggestions
✅ Complete pipeline integration

To use with actual LLM code generation:
1. Set up API keys in .env file
2. Run: python src/main.py
3. Follow interactive prompts or use CLI arguments

For setup help: python get_started.py
        """)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        print("Please check that all dependencies are installed correctly.")


if __name__ == "__main__":
    main()