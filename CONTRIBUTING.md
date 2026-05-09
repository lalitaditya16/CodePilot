# Contributing to AI Python Code Generator

First off, thank you for considering contributing to our project! 🎉

## 🚀 How to Contribute

### 🐛 Reporting Bugs
- Use the GitHub Issues page
- Include Python version, OS, and error messages
- Provide steps to reproduce the issue

### 💡 Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Include examples if possible

### 🔧 Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**: `pytest`
6. **Check code quality**: `black src/ && flake8 src/`
7. **Commit your changes**: `git commit -m 'Add amazing feature'`
8. **Push to your branch**: `git push origin feature/amazing-feature`
9. **Open a Pull Request**

### 📝 Code Style
- Follow PEP 8
- Use Black for formatting
- Add type hints
- Write docstrings for functions and classes
- Keep functions focused and small

### 🧪 Testing
- Write tests for new features
- Ensure all tests pass
- Maintain test coverage above 80%

## 🏗️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-python-code-generator.git
cd ai-python-code-generator

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## 📋 Pull Request Checklist

- [ ] Code follows the project's style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Commit messages are descriptive
- [ ] No merge conflicts

## 🤝 Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

Thank you for contributing! 🙏