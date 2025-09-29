"""
Main Application Entry Point

This module provides the main interface for the Python Code Generator with LLM integration.
It orchestrates code generation, validation, testing, and optimization workflows.
"""

import os
import sys
import argparse
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Add src and parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import our modules
from code_generator import CodeGenerator, CodeGenerationRequest
from code_validator import CodeValidator
from test_generator import TestGenerator
from code_optimizer import CodeOptimizer
from config.settings import settings

# Rich for better console output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    console = Console()
except ImportError:
    console = None


class CodeGenerationPipeline:
    """Main pipeline that orchestrates the entire code generation process."""
    
    def __init__(self):
        self.generator = CodeGenerator()
        self.validator = CodeValidator()
        self.test_generator = TestGenerator()
        self.optimizer = CodeOptimizer()
        
        # Create output directories
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary output directories."""
        directories = [
            settings.GENERATED_CODE_DIR,
            settings.TEST_OUTPUT_DIR,
            "reports"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def run_full_pipeline(self, description: str, **kwargs) -> Dict[str, Any]:
        """Run the complete code generation pipeline."""
        results = {
            'description': description,
            'timestamp': time.time(),
            'stages': {}
        }
        
        if console:
            console.print(Panel(f"Starting Code Generation Pipeline\n[bold blue]{description}[/bold blue]", 
                              title="🚀 AI Code Generator"))
        
        # Stage 1: Code Generation
        with self._progress_context("Generating code with LLM..."):
            generation_result = self._generate_code(description, **kwargs)
            results['stages']['generation'] = generation_result
        
        if not generation_result['success']:
            return results
        
        generated_code = generation_result['code']
        
        # Stage 2: Code Validation
        with self._progress_context("Validating code quality..."):
            validation_result = self._validate_code(generated_code)
            results['stages']['validation'] = validation_result
        
        # Stage 3: Test Generation and Execution
        with self._progress_context("Generating and running tests..."):
            testing_result = self._test_code(generated_code)
            results['stages']['testing'] = testing_result
        
        # Stage 4: Code Optimization
        with self._progress_context("Optimizing code..."):
            optimization_result = self._optimize_code(generated_code)
            results['stages']['optimization'] = optimization_result
        
        # Stage 5: Generate Reports
        with self._progress_context("Generating reports..."):
            report_result = self._generate_reports(results)
            results['stages']['reporting'] = report_result
        
        # Display summary
        self._display_summary(results)
        
        return results
    
    def _generate_code(self, description: str, **kwargs) -> Dict[str, Any]:
        """Generate code using LLM."""
        try:
            request = CodeGenerationRequest(
                description=description,
                function_name=kwargs.get('function_name'),
                parameters=kwargs.get('parameters'),
                return_type=kwargs.get('return_type'),
                additional_requirements=kwargs.get('additional_requirements')
            )
            
            result = self.generator.generate(request)
            
            # Save generated code
            filename = f"generated_{int(time.time())}.py"
            filepath = os.path.join(settings.GENERATED_CODE_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result.code)
            
            return {
                'success': True,
                'code': result.code,
                'function_name': result.function_name,
                'complexity': result.estimated_complexity,
                'dependencies': result.dependencies,
                'warnings': result.warnings,
                'filepath': filepath
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'code': None
            }
    
    def _validate_code(self, code: str) -> Dict[str, Any]:
        """Validate generated code."""
        try:
            validation_result = self.validator.validate(code)
            
            return {
                'success': validation_result.is_valid,
                'syntax_errors': validation_result.syntax_errors,
                'style_issues': validation_result.style_issues,
                'type_errors': validation_result.type_errors,
                'security_issues': validation_result.security_issues,
                'complexity_score': validation_result.complexity_score,
                'maintainability_index': validation_result.maintainability_index,
                'pylint_score': validation_result.pylint_score,
                'suggestions': validation_result.suggestions,
                'formatted_code': validation_result.formatted_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _test_code(self, code: str) -> Dict[str, Any]:
        """Generate and run tests for the code."""
        try:
            test_results = self.test_generator.generate_and_run_tests(code)
            
            # Calculate summary statistics
            total_tests = sum(result['execution_result'].total for result in test_results.values())
            total_passed = sum(result['execution_result'].passed for result in test_results.values())
            total_failed = sum(result['execution_result'].failed for result in test_results.values())
            
            success_rate = (total_passed / max(total_tests, 1)) * 100
            
            return {
                'success': total_failed == 0,
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'success_rate': success_rate,
                'detailed_results': test_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_tests': 0,
                'passed': 0,
                'failed': 1
            }
    
    def _optimize_code(self, code: str) -> Dict[str, Any]:
        """Optimize the generated code."""
        try:
            optimization_result = self.optimizer.optimize(code)
            
            return {
                'success': True,
                'optimization_score': optimization_result.optimization_score,
                'suggestions_count': len(optimization_result.suggestions),
                'optimized_code': optimization_result.optimized_code,
                'suggestions': [
                    {
                        'type': s.type,
                        'description': s.description,
                        'confidence': s.confidence,
                        'improvement': s.estimated_improvement
                    }
                    for s in optimization_result.suggestions[:5]  # Top 5
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'optimization_score': 0.0
            }
    
    def _generate_reports(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive reports."""
        try:
            timestamp = int(results['timestamp'])
            
            # Generate JSON report
            json_report_path = f"reports/report_{timestamp}.json"
            with open(json_report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Generate Markdown report
            markdown_report = self._create_markdown_report(results)
            markdown_report_path = f"reports/report_{timestamp}.md"
            with open(markdown_report_path, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            
            return {
                'success': True,
                'json_report': json_report_path,
                'markdown_report': markdown_report_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_markdown_report(self, results: Dict[str, Any]) -> str:
        """Create a comprehensive markdown report."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['timestamp']))
        
        report_lines = [
            f"# Code Generation Report",
            f"**Generated:** {timestamp}",
            f"**Description:** {results['description']}",
            "",
            "## Summary",
            ""
        ]
        
        # Generation Summary
        gen_result = results['stages'].get('generation', {})
        if gen_result.get('success'):
            report_lines.extend([
                f"✅ **Code Generation:** Success",
                f"- Function: `{gen_result.get('function_name', 'N/A')}`",
                f"- Complexity: {gen_result.get('complexity', 0)}",
                f"- Dependencies: {len(gen_result.get('dependencies', []))}",
                f"- Warnings: {len(gen_result.get('warnings', []))}",
                ""
            ])
        else:
            report_lines.extend([
                f"❌ **Code Generation:** Failed",
                f"- Error: {gen_result.get('error', 'Unknown error')}",
                ""
            ])
        
        # Validation Summary
        val_result = results['stages'].get('validation', {})
        if val_result.get('success'):
            report_lines.extend([
                f"✅ **Code Validation:** Passed",
                f"- Pylint Score: {val_result.get('pylint_score', 0):.1f}/10",
                f"- Complexity: {val_result.get('complexity_score', 0):.1f}",
                f"- Maintainability: {val_result.get('maintainability_index', 0):.1f}",
                ""
            ])
        else:
            issues_count = (len(val_result.get('syntax_errors', [])) + 
                          len(val_result.get('style_issues', [])) + 
                          len(val_result.get('type_errors', [])))
            report_lines.extend([
                f"⚠️ **Code Validation:** Issues Found ({issues_count})",
                ""
            ])
        
        # Testing Summary
        test_result = results['stages'].get('testing', {})
        report_lines.extend([
            f"🧪 **Testing:** {test_result.get('passed', 0)}/{test_result.get('total_tests', 0)} passed "
            f"({test_result.get('success_rate', 0):.1f}%)",
            ""
        ])
        
        # Optimization Summary
        opt_result = results['stages'].get('optimization', {})
        if opt_result.get('success'):
            report_lines.extend([
                f"⚡ **Optimization:** Score {opt_result.get('optimization_score', 0):.1f}/100",
                f"- Suggestions: {opt_result.get('suggestions_count', 0)}",
                ""
            ])
        
        # Detailed sections would go here...
        report_lines.extend([
            "## Generated Code",
            "",
            "```python",
            gen_result.get('code', 'No code generated'),
            "```",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def _progress_context(self, description: str):
        """Context manager for progress indication."""
        if console:
            return console.status(description, spinner="dots")
        else:
            print(f"{description}")
            return self._dummy_context()
    
    def _dummy_context(self):
        """Dummy context manager for when rich is not available."""
        class DummyContext:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return DummyContext()
    
    def _display_summary(self, results: Dict[str, Any]):
        """Display pipeline summary."""
        if not console:
            print("\n" + "="*50)
            print("PIPELINE SUMMARY")
            print("="*50)
            return
        
        # Create summary table
        table = Table(title="Pipeline Results Summary")
        table.add_column("Stage", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")
        
        stages = results['stages']
        
        # Generation
        gen_result = stages.get('generation', {})
        gen_status = "✅ Success" if gen_result.get('success') else "❌ Failed"
        gen_details = f"Function: {gen_result.get('function_name', 'N/A')}"
        table.add_row("Code Generation", gen_status, gen_details)
        
        # Validation
        val_result = stages.get('validation', {})
        val_status = "✅ Valid" if val_result.get('success') else "⚠️ Issues"
        val_details = f"Pylint: {val_result.get('pylint_score', 0):.1f}/10"
        table.add_row("Validation", val_status, val_details)
        
        # Testing
        test_result = stages.get('testing', {})
        test_status = f"{test_result.get('success_rate', 0):.1f}% passed"
        test_details = f"{test_result.get('passed', 0)}/{test_result.get('total_tests', 0)} tests"
        table.add_row("Testing", test_status, test_details)
        
        # Optimization
        opt_result = stages.get('optimization', {})
        opt_status = f"{opt_result.get('optimization_score', 0):.1f}/100"
        opt_details = f"{opt_result.get('suggestions_count', 0)} suggestions"
        table.add_row("Optimization", opt_status, opt_details)
        
        console.print(table)
        
        # Show generated code
        if gen_result.get('success') and gen_result.get('code'):
            syntax = Syntax(gen_result['code'], "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Generated Code"))


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Python Code Generator with Validation, Testing, and Optimization"
    )
    
    parser.add_argument(
        "description",
        help="Natural language description of the code to generate"
    )
    
    parser.add_argument(
        "--function-name",
        help="Specific function name to use"
    )
    
    parser.add_argument(
        "--parameters",
        nargs="*",
        help="Function parameters (e.g., 'n: int' 'arr: List[int]')"
    )
    
    parser.add_argument(
        "--return-type",
        help="Expected return type"
    )
    
    parser.add_argument(
        "--requirements",
        help="Additional requirements or constraints"
    )
    
    parser.add_argument(
        "--provider",
        choices=['openai', 'anthropic'],
        default=settings.DEFAULT_LLM_PROVIDER,
        help="LLM provider to use"
    )
    
    parser.add_argument(
        "--output-dir",
        default=settings.GENERATED_CODE_DIR,
        help="Output directory for generated files"
    )
    
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip test generation and execution"
    )
    
    parser.add_argument(
        "--skip-optimization",
        action="store_true",
        help="Skip code optimization"
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = CodeGenerationPipeline()
    
    # Override settings if specified
    if args.provider:
        pipeline.generator = CodeGenerator(args.provider)
    
    # Run pipeline
    try:
        results = pipeline.run_full_pipeline(
            description=args.description,
            function_name=args.function_name,
            parameters=args.parameters,
            return_type=args.return_type,
            additional_requirements=args.requirements
        )
        
        # Print final status
        if console:
            if results['stages']['generation'].get('success'):
                console.print("🎉 [bold green]Pipeline completed successfully![/bold green]")
                console.print(f"📁 Check the reports directory for detailed analysis")
            else:
                console.print("💥 [bold red]Pipeline failed during code generation[/bold red]")
        else:
            print("\nPipeline completed!")
            print(f"Check {args.output_dir} for generated code")
    
    except KeyboardInterrupt:
        if console:
            console.print("\n⚠️ [yellow]Pipeline interrupted by user[/yellow]")
        else:
            print("\nPipeline interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        if console:
            console.print(f"💥 [bold red]Pipeline failed: {str(e)}[/bold red]")
        else:
            print(f"Pipeline failed: {str(e)}")
        sys.exit(1)


def interactive_mode():
    """Run in interactive mode for easier usage."""
    if console:
        console.print(Panel(
            "Welcome to the AI Code Generator!\n"
            "This tool will generate Python code, validate it, test it, and optimize it for you.",
            title="🤖 AI Code Generator"
        ))
    else:
        print("Welcome to the AI Code Generator!")
    
    pipeline = CodeGenerationPipeline()
    
    while True:
        try:
            if console:
                console.print("\n[bold cyan]What would you like me to generate?[/bold cyan]")
            
            description = input("Describe the code you want: ").strip()
            
            if not description or description.lower() in ['quit', 'exit', 'q']:
                break
            
            # Run pipeline
            results = pipeline.run_full_pipeline(description)
            
            # Ask if user wants to continue
            if console:
                console.print("\n[dim]Press Enter to generate more code, or 'q' to quit[/dim]")
            
            continue_input = input().strip().lower()
            if continue_input in ['q', 'quit', 'exit']:
                break
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    if console:
        console.print("👋 [bold blue]Thanks for using AI Code Generator![/bold blue]")
    else:
        print("Thanks for using AI Code Generator!")


if __name__ == "__main__":
    # Check if running with arguments or in interactive mode
    if len(sys.argv) > 1:
        main()
    else:
        interactive_mode()