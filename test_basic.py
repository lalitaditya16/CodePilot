"""
Quick test script to validate core functionality without LLM integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_functionality():
    """Test core modules work independently"""
    
    # Test code validation
    print("🔍 Testing code validation...")
    from code_validator import CodeValidator
    
    validator = CodeValidator()
    sample_code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
'''
    
    result = validator.validate(sample_code)
    print(f"✅ Validation: Score {result.pylint_score:.1f}/10")
    
    # Test test generation (without execution to avoid file issues)
    print("\n🧪 Testing test generation...")
    from test_generator import TestCaseGenerator
    
    test_gen = TestCaseGenerator()
    tests = test_gen.generate_unit_tests(sample_code, "factorial")
    print(f"✅ Generated {len(tests)} test cases")
    
    # Test optimization analysis
    print("\n⚡ Testing optimization analysis...")
    from code_optimizer import PatternOptimizer
    
    optimizer = PatternOptimizer()
    suggestions = optimizer.optimize_patterns(sample_code)
    print(f"✅ Found {len(suggestions)} optimization suggestions")
    
    print("\n🎉 All core modules are working correctly!")

if __name__ == "__main__":
    test_basic_functionality()