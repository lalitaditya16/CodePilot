# 🤖 AI Python Code Generator

> **Generate • Validate • Test • Optimize Python Code with AI**

A comprehensive Python code generation tool powered by Large Language Models (LLMs) that automatically generates, validates, tests, and optimizes Python code with professional-grade quality analysis.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude-purple.svg)

## ✨ Features

### 🎯 **Intelligent Code Generation**
- **Multi-LLM Support**: OpenAI GPT-4 and Anthropic Claude integration
- **Context-Aware**: Understands requirements and generates appropriate code
- **Customizable**: Specify function names, return types, and requirements

### 🔍 **Comprehensive Code Validation**
- **Syntax Analysis**: AST-based syntax error detection
- **Style Checking**: PEP 8 compliance with Black, Flake8, Pylint
- **Type Safety**: MyPy static type checking
- **Security Scanning**: Bandit security vulnerability detection
- **Complexity Analysis**: Cyclomatic complexity and maintainability metrics

### 🧪 **Automated Testing**
- **Smart Test Generation**: Creates relevant unit tests automatically
- **Property-Based Testing**: Hypothesis integration for robust testing
- **Test Execution**: Runs tests and provides detailed results
- **Coverage Analysis**: Tracks test coverage and effectiveness

### ⚡ **Performance Optimization**
- **Pattern Detection**: Identifies common performance anti-patterns
- **Memory Analysis**: Memory usage optimization suggestions
- **Algorithm Improvements**: Suggests more efficient algorithms
- **Refactoring Recommendations**: Code structure improvements

### 🌐 **Modern Web Interface**
- **Streamlit Web App**: Beautiful, interactive web interface
- **Real-time Feedback**: Live validation and progress tracking
- **Visual Analytics**: Charts and metrics for code quality
- **Export Capabilities**: Download generated code and reports

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── code_generator.py      # LLM integration for code generation
│   ├── code_validator.py      # Code validation and quality checks
│   ├── test_generator.py      # Test case generation and execution
│   ├── code_optimizer.py      # Code optimization and refactoring
│   └── main.py               # Main application entry point
├── tests/
│   ├── __init__.py
│   ├── test_code_generator.py
│   ├── test_code_validator.py
│   ├── test_test_generator.py
│   └── test_code_optimizer.py
├── examples/
│   ├── generated_code/       # Examples of generated code
│   └── sample_prompts.py     # Sample prompts for testing
├── config/
│   └── settings.py          # Configuration settings
├── requirements.txt
├── setup.py
└── README.md
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your LLM API keys in `config/settings.py`
4. Run: `python src/main.py`

## Usage

```python
from src.code_generator import CodeGenerator

# Initialize the code generator
generator = CodeGenerator()

# Generate code from description
code = generator.generate("Create a function to calculate fibonacci numbers")

# Validate the generated code
validator = CodeValidator()
validation_results = validator.validate(code)

# Generate and run tests
test_gen = TestGenerator()
tests = test_gen.generate_tests(code)
results = test_gen.run_tests(tests)

# Optimize the code
optimizer = CodeOptimizer()
optimized_code = optimizer.optimize(code)
```

## Configuration

Set up your configuration in `config/settings.py`:
- LLM API keys (OpenAI, Anthropic, etc.)
- Code quality thresholds
- Test coverage requirements
- Optimization preferences