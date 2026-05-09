"""
Getting Started Script for Python Code Generator

This script helps you set up and test the Python Code Generator project.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_banner():
    """Print welcome banner."""
    print("""
╭─────────────────────────────────────────────────────────────╮
│                                                             │
│   🤖 Python Code Generator with LLM Integration            │
│                                                             │
│   Generate • Validate • Test • Optimize Python Code       │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
    """)


def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("   Try running: pip install -r requirements.txt")
        return False


def setup_environment():
    """Set up environment configuration."""
    print("\n🔧 Setting up environment...")
    
    # Copy .env.example to .env if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your API keys!")
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    # Create necessary directories
    directories = [
        "examples/generated_code",
        "test_results",
        "reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")
    return True


def test_installation():
    """Test the installation with a simple example."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        sys.path.insert(0, "src")
        
        from code_generator import CodeGenerator
        from code_validator import CodeValidator
        from test_generator import TestGenerator
        from code_optimizer import CodeOptimizer
        
        print("✅ All modules imported successfully")
        
        # Test basic functionality (without API calls)
        print("🔍 Testing basic functionality...")
        
        # Test code validator with sample code
        validator = CodeValidator()
        sample_code = '''
def hello_world():
    """A simple hello world function."""
    return "Hello, World!"
'''
        
        result = validator.validate(sample_code)
        print(f"✅ Code validation test passed (Pylint score: {result.pylint_score:.1f})")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_usage_examples():
    """Show usage examples."""
    print("""
🚀 Quick Start Examples:

1. Interactive Mode (recommended for beginners):
   python src/main.py

2. Command Line Usage:
   python src/main.py "Create a function to calculate fibonacci numbers"

3. With specific parameters:
   python src/main.py "Create a binary search function" --function-name binary_search --return-type int

4. Advanced usage:
   python src/main.py "Sort an array" --provider openai --requirements "Use quicksort algorithm"

📁 Project Structure:
   src/              - Main source code
   tests/            - Unit tests
   examples/         - Sample code and prompts
   config/           - Configuration files
   reports/          - Generated reports
   requirements.txt  - Python dependencies

⚙️  Configuration:
   1. Edit .env file to add your API keys
   2. Modify config/settings.py for advanced settings

🔑 API Keys Required:
   - OpenAI API key (for GPT models)
   - Anthropic API key (for Claude models, optional)

📚 Example Prompts:
   - "Create a function to calculate factorial"
   - "Implement binary search algorithm"
   - "Write a class for a binary tree"
   - "Create a function to validate email addresses"
    """)


def run_example():
    """Run a simple example without API calls."""
    print("\n🎯 Running example without API calls...")
    
    try:
        sys.path.insert(0, "src")
        from code_validator import CodeValidator
        from test_generator import TestGenerator
        from code_optimizer import CodeOptimizer
        
        # Sample code to analyze
        sample_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number using recursion."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n-1)
'''
        
        print("📊 Analyzing sample code...")
        
        # Validate code
        validator = CodeValidator()
        validation_result = validator.validate(sample_code)
        
        print(f"   Validation: {'✅ Passed' if validation_result.is_valid else '⚠️ Issues found'}")
        print(f"   Pylint Score: {validation_result.pylint_score:.1f}/10")
        print(f"   Complexity: {validation_result.complexity_score:.1f}")
        print(f"   Suggestions: {len(validation_result.suggestions)}")
        
        # Generate tests
        test_gen = TestGenerator()
        test_results = test_gen.generate_and_run_tests(sample_code)
        
        total_tests = sum(result['execution_result'].total for result in test_results.values())
        total_passed = sum(result['execution_result'].passed for result in test_results.values())
        
        print(f"   Tests Generated: {total_tests}")
        print(f"   Tests Passed: {total_passed}/{total_tests}")
        
        # Optimize code
        optimizer = CodeOptimizer()
        opt_result = optimizer.optimize(sample_code)
        
        print(f"   Optimization Score: {opt_result.optimization_score:.1f}/100")
        print(f"   Optimization Suggestions: {len(opt_result.suggestions)}")
        
        if opt_result.suggestions:
            print("\n   Top suggestions:")
            for i, suggestion in enumerate(opt_result.suggestions[:3], 1):
                print(f"   {i}. {suggestion.description}")
        
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")


def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  You can try installing dependencies manually:")
        print("   pip install -r requirements.txt")
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Installation test failed. Some features may not work correctly.")
    
    # Run example
    run_example()
    
    # Show usage examples
    show_usage_examples()
    
    print("""
🎉 Setup completed!

Next steps:
1. Add your API keys to the .env file
2. Run: python src/main.py
3. Follow the interactive prompts

For help: python src/main.py --help
    """)
    
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check the error messages above and try again.")