"""
Code Generator Module

This module handles LLM integration for generating Python code from natural language descriptions.
"""

import openai
import anthropic
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import re
from config.settings import settings


@dataclass
class CodeGenerationRequest:
    """Request object for code generation."""
    description: str
    function_name: Optional[str] = None
    parameters: Optional[List[str]] = None
    return_type: Optional[str] = None
    additional_requirements: Optional[str] = None


@dataclass
class GeneratedCode:
    """Container for generated code and metadata."""
    code: str
    description: str
    function_name: str
    estimated_complexity: int
    dependencies: List[str]
    warnings: List[str]


class LLMProvider:
    """Base class for LLM providers."""
    
    def generate_code(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider for code generation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate_code(self, prompt: str) -> str:
        """Generate code using OpenAI GPT."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert Python developer. Generate clean, well-documented, 
                        and efficient Python code based on the user's requirements. Follow PEP 8 standards 
                        and include appropriate docstrings. Return only the Python code without markdown 
                        formatting or explanations."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider for code generation."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_code(self, prompt: str) -> str:
        """Generate code using Anthropic Claude."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                messages=[{
                    "role": "user",
                    "content": f"""You are an expert Python developer. Generate clean, well-documented, 
                    and efficient Python code based on the following requirements. Follow PEP 8 standards 
                    and include appropriate docstrings. Return only the Python code without markdown 
                    formatting or explanations.
                    
                    Requirements: {prompt}"""
                }]
            )
            return message.content[0].text.strip()
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")


class CodeGenerator:
    """Main code generation class that orchestrates LLM providers."""
    
    def __init__(self, provider: str = None):
        self.provider = self._initialize_provider(provider or settings.DEFAULT_LLM_PROVIDER)
    
    def _initialize_provider(self, provider_name: str) -> LLMProvider:
        """Initialize the specified LLM provider."""
        if provider_name.lower() == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            return OpenAIProvider(settings.OPENAI_API_KEY, settings.DEFAULT_MODEL)
        elif provider_name.lower() == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not configured")
            return AnthropicProvider(settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    def generate(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code from a structured request."""
        prompt = self._build_prompt(request)
        raw_code = self.provider.generate_code(prompt)
        
        # Clean and parse the generated code
        cleaned_code = self._clean_code(raw_code)
        
        # Extract metadata
        function_name = self._extract_function_name(cleaned_code) or request.function_name or "generated_function"
        dependencies = self._extract_dependencies(cleaned_code)
        complexity = self._estimate_complexity(cleaned_code)
        warnings = self._check_potential_issues(cleaned_code)
        
        return GeneratedCode(
            code=cleaned_code,
            description=request.description,
            function_name=function_name,
            estimated_complexity=complexity,
            dependencies=dependencies,
            warnings=warnings
        )
    
    def generate_simple(self, description: str) -> str:
        """Simple interface for quick code generation."""
        request = CodeGenerationRequest(description=description)
        result = self.generate(request)
        return result.code
    
    def _build_prompt(self, request: CodeGenerationRequest) -> str:
        """Build a comprehensive prompt for code generation."""
        prompt_parts = [f"Generate Python code for: {request.description}"]
        
        if request.function_name:
            prompt_parts.append(f"Function name should be: {request.function_name}")
        
        if request.parameters:
            prompt_parts.append(f"Function parameters: {', '.join(request.parameters)}")
        
        if request.return_type:
            prompt_parts.append(f"Return type: {request.return_type}")
        
        if request.additional_requirements:
            prompt_parts.append(f"Additional requirements: {request.additional_requirements}")
        
        prompt_parts.extend([
            "Requirements:",
            "- Follow PEP 8 style guidelines",
            "- Include comprehensive docstrings",
            "- Add type hints where appropriate",
            "- Handle edge cases and errors gracefully",
            "- Write efficient and readable code",
            "- Include inline comments for complex logic"
        ])
        
        return "\n".join(prompt_parts)
    
    def _clean_code(self, raw_code: str) -> str:
        """Clean and format the generated code."""
        # Remove markdown code blocks if present
        code = re.sub(r'```python\n|```\n|```', '', raw_code)
        
        # Remove extra whitespace and normalize indentation
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines at the beginning
            if not cleaned_lines and not line.strip():
                continue
            cleaned_lines.append(line.rstrip())
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def _extract_function_name(self, code: str) -> Optional[str]:
        """Extract the main function name from generated code."""
        match = re.search(r'def\s+(\w+)\s*\(', code)
        return match.group(1) if match else None
    
    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract import dependencies from the code."""
        dependencies = []
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import '):
                dep = line.replace('import ', '').split()[0]
                dependencies.append(dep)
            elif line.startswith('from '):
                match = re.match(r'from\s+(\w+)', line)
                if match:
                    dependencies.append(match.group(1))
        
        return list(set(dependencies))
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate code complexity based on control structures."""
        complexity = 1  # Base complexity
        
        # Count control structures that increase complexity
        control_structures = [
            'if ', 'elif ', 'for ', 'while ', 'try:', 'except', 'with ', 'and ', 'or '
        ]
        
        for structure in control_structures:
            complexity += code.count(structure)
        
        return min(complexity, 20)  # Cap at 20
    
    def _check_potential_issues(self, code: str) -> List[str]:
        """Check for potential issues in the generated code."""
        warnings = []
        
        # Check for common issues
        if 'eval(' in code or 'exec(' in code:
            warnings.append("Code contains eval() or exec() which may be unsafe")
        
        if 'import os' in code and ('os.system' in code or 'os.popen' in code):
            warnings.append("Code uses potentially unsafe os operations")
        
        if code.count('\n') > 100:
            warnings.append("Generated code is quite long, consider breaking into smaller functions")
        
        if not re.search(r'""".*?"""', code, re.DOTALL) and not re.search(r"'''.*?'''", code, re.DOTALL):
            if 'def ' in code:
                warnings.append("Function missing docstring")
        
        return warnings


# Example usage and testing functions
def example_usage():
    """Example usage of the CodeGenerator."""
    generator = CodeGenerator()
    
    # Simple generation
    code1 = generator.generate_simple("Create a function to calculate the factorial of a number")
    print("Simple generation:")
    print(code1)
    print("\n" + "="*50 + "\n")
    
    # Structured generation
    request = CodeGenerationRequest(
        description="Create a binary search function",
        function_name="binary_search",
        parameters=["arr: List[int]", "target: int"],
        return_type="int",
        additional_requirements="Return -1 if not found, include error handling"
    )
    
    result = generator.generate(request)
    print("Structured generation:")
    print(f"Function: {result.function_name}")
    print(f"Complexity: {result.estimated_complexity}")
    print(f"Dependencies: {result.dependencies}")
    print(f"Warnings: {result.warnings}")
    print(f"Code:\n{result.code}")


if __name__ == "__main__":
    example_usage()