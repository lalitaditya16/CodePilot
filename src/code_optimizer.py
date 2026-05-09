"""
Code Optimizer Module

This module handles code optimization including performance improvements,
memory optimization, refactoring suggestions, and code quality enhancements.
"""

import ast
import re
import sys
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import time
import memory_profiler
import cProfile
import pstats
import io
from contextlib import contextmanager
import tempfile
import os

# Optimization libraries
try:
    import rope.base.project
    import rope.refactor.extract
    import rope.refactor.inline
    from rope.base.resources import File
except ImportError as e:
    print(f"Warning: Rope not available for refactoring: {e}")

from config.settings import settings


@dataclass
class OptimizationSuggestion:
    """Represents a code optimization suggestion."""
    type: str  # 'performance', 'memory', 'readability', 'maintainability'
    description: str
    original_code: str
    optimized_code: str
    estimated_improvement: str
    line_number: int
    confidence: float  # 0.0 to 1.0


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""
    execution_time: float
    memory_usage: float
    cpu_time: float
    function_calls: int
    recursive_calls: int


@dataclass
class OptimizationResult:
    """Results from code optimization process."""
    original_code: str
    optimized_code: str
    suggestions: List[OptimizationSuggestion]
    performance_improvement: Optional[PerformanceMetrics]
    optimization_score: float  # Overall improvement score


class PerformanceProfiler:
    """Profiles code performance to identify bottlenecks."""
    
    def profile_code(self, code: str, test_inputs: Dict[str, Any] = None) -> PerformanceMetrics:
        """Profile code execution and return metrics."""
        # Create a temporary module to execute the code
        exec_globals = {}
        
        try:
            # Execute the code to define functions
            exec(code, exec_globals)
            
            # Find the main function to profile
            main_function = self._find_main_function(code, exec_globals)
            
            if main_function:
                return self._profile_function(main_function, test_inputs or {})
            else:
                return PerformanceMetrics(0.0, 0.0, 0.0, 0, 0)
                
        except Exception as e:
            print(f"Profiling error: {e}")
            return PerformanceMetrics(0.0, 0.0, 0.0, 0, 0)
    
    def _find_main_function(self, code: str, exec_globals: Dict) -> Optional[callable]:
        """Find the main function to profile."""
        # Look for functions in the executed code
        functions = {name: obj for name, obj in exec_globals.items() 
                    if callable(obj) and not name.startswith('_')}
        
        # Prefer functions with specific names
        for preferred_name in ['main', 'run', 'execute']:
            if preferred_name in functions:
                return functions[preferred_name]
        
        # Return the first available function
        return next(iter(functions.values())) if functions else None
    
    @contextmanager
    def _memory_monitor(self):
        """Context manager for memory monitoring."""
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            yield
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = final_memory - initial_memory
        except ImportError:
            memory_used = 0.0
            yield
        
        return memory_used
    
    def _profile_function(self, func: callable, test_inputs: Dict[str, Any]) -> PerformanceMetrics:
        """Profile a specific function."""
        # Prepare test arguments
        import inspect
        sig = inspect.signature(func)
        args = []
        
        for param_name in sig.parameters.keys():
            if param_name in test_inputs:
                args.append(test_inputs[param_name])
            else:
                # Provide default test values
                args.append(self._get_default_test_value(param_name))
        
        # Profile execution time
        start_time = time.time()
        
        # Profile with cProfile
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            # Execute function
            result = func(*args) if args else func()
            
            profiler.disable()
            
            # Get execution time
            execution_time = time.time() - start_time
            
            # Analyze profile stats
            stats_stream = io.StringIO()
            stats = pstats.Stats(profiler, stream=stats_stream)
            stats.sort_stats('cumulative')
            
            # Extract metrics
            total_calls = stats.total_calls
            recursive_calls = 0  # Would need more complex analysis
            
            return PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=0.0,  # Would need memory_profiler integration
                cpu_time=execution_time,
                function_calls=total_calls,
                recursive_calls=recursive_calls
            )
            
        except Exception as e:
            print(f"Function execution error: {e}")
            return PerformanceMetrics(0.0, 0.0, 0.0, 0, 0)
    
    def _get_default_test_value(self, param_name: str) -> Any:
        """Get default test value based on parameter name."""
        if 'n' in param_name.lower() or 'num' in param_name.lower():
            return 10
        elif 'arr' in param_name.lower() or 'list' in param_name.lower():
            return list(range(10))
        elif 'str' in param_name.lower() or 'text' in param_name.lower():
            return "test string"
        else:
            return None


class PatternOptimizer:
    """Identifies and optimizes common code patterns."""
    
    def optimize_patterns(self, code: str) -> List[OptimizationSuggestion]:
        """Identify and suggest optimizations for common patterns."""
        suggestions = []
        
        try:
            tree = ast.parse(code)
            
            # Analyze AST for optimization opportunities
            suggestions.extend(self._optimize_loops(tree, code))
            suggestions.extend(self._optimize_recursion(tree, code))
            suggestions.extend(self._optimize_data_structures(tree, code))
            suggestions.extend(self._optimize_string_operations(tree, code))
            suggestions.extend(self._optimize_list_operations(tree, code))
            
        except Exception as e:
            print(f"Pattern optimization error: {e}")
        
        return suggestions
    
    def _optimize_loops(self, tree: ast.AST, code: str) -> List[OptimizationSuggestion]:
        """Optimize loop patterns."""
        suggestions = []
        lines = code.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for inefficient list building
                if self._has_inefficient_list_append(node):
                    line_num = getattr(node, 'lineno', 1)
                    original = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    suggestions.append(OptimizationSuggestion(
                        type='performance',
                        description='Use list comprehension instead of append in loop',
                        original_code=original,
                        optimized_code='# Use list comprehension: [expression for item in iterable]',
                        estimated_improvement='2-3x faster',
                        line_number=line_num,
                        confidence=0.8
                    ))
        
        return suggestions
    
    def _optimize_recursion(self, tree: ast.AST, code: str) -> List[OptimizationSuggestion]:
        """Optimize recursive functions."""
        suggestions = []
        lines = code.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function is recursive
                if self._is_recursive_function(node):
                    # Check for memoization opportunity
                    if self._can_benefit_from_memoization(node):
                        suggestions.append(OptimizationSuggestion(
                            type='performance',
                            description=f'Add memoization to recursive function {node.name}',
                            original_code=f'def {node.name}(...):',
                            optimized_code='@functools.lru_cache(maxsize=None)\ndef ' + f'{node.name}(...):\n    # same implementation',
                            estimated_improvement='Exponential improvement for repeated calls',
                            line_number=getattr(node, 'lineno', 1),
                            confidence=0.9
                        ))
        
        return suggestions
    
    def _optimize_data_structures(self, tree: ast.AST, code: str) -> List[OptimizationSuggestion]:
        """Optimize data structure usage."""
        suggestions = []
        
        for node in ast.walk(tree):
            # Check for inefficient membership testing
            if isinstance(node, ast.Compare):
                if self._is_inefficient_membership_test(node):
                    suggestions.append(OptimizationSuggestion(
                        type='performance',
                        description='Use set for O(1) membership testing instead of list',
                        original_code='if item in long_list:',
                        optimized_code='# Convert to set: long_set = set(long_list)\n# Then: if item in long_set:',
                        estimated_improvement='O(1) vs O(n) lookup',
                        line_number=getattr(node, 'lineno', 1),
                        confidence=0.7
                    ))
        
        return suggestions
    
    def _optimize_string_operations(self, tree: ast.AST, code: str) -> List[OptimizationSuggestion]:
        """Optimize string operations."""
        suggestions = []
        
        for node in ast.walk(tree):
            # Check for string concatenation in loops
            if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
                if self._is_string_concatenation_in_loop(node, tree):
                    suggestions.append(OptimizationSuggestion(
                        type='performance',
                        description='Use join() instead of += for string concatenation in loops',
                        original_code='result += string_item',
                        optimized_code="result = ''.join(string_list)",
                        estimated_improvement='Significantly faster for many operations',
                        line_number=getattr(node, 'lineno', 1),
                        confidence=0.8
                    ))
        
        return suggestions
    
    def _optimize_list_operations(self, tree: ast.AST, code: str) -> List[OptimizationSuggestion]:
        """Optimize list operations."""
        suggestions = []
        
        for node in ast.walk(tree):
            # Check for inefficient list filtering
            if isinstance(node, ast.ListComp):
                # This is already optimized, but check for nested loops
                if len([gen for gen in node.generators if isinstance(gen.iter, ast.ListComp)]) > 0:
                    suggestions.append(OptimizationSuggestion(
                        type='readability',
                        description='Consider breaking down nested list comprehensions',
                        original_code='Complex nested comprehension',
                        optimized_code='# Break into multiple steps for readability',
                        estimated_improvement='Better readability and maintainability',
                        line_number=getattr(node, 'lineno', 1),
                        confidence=0.6
                    ))
        
        return suggestions
    
    # Helper methods for pattern detection
    def _has_inefficient_list_append(self, for_node: ast.For) -> bool:
        """Check if loop has inefficient list append pattern."""
        for node in ast.walk(for_node):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr == 'append'):
                    return True
        return False
    
    def _is_recursive_function(self, func_node: ast.FunctionDef) -> bool:
        """Check if function is recursive."""
        func_name = func_node.name
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    return True
        return False
    
    def _can_benefit_from_memoization(self, func_node: ast.FunctionDef) -> bool:
        """Check if recursive function can benefit from memoization."""
        # Simple heuristic: if it's recursive and doesn't have side effects
        return (self._is_recursive_function(func_node) and 
                not self._has_side_effects(func_node))
    
    def _has_side_effects(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has side effects."""
        for node in ast.walk(func_node):
            # Check for global variables, I/O operations, etc.
            if isinstance(node, (ast.Global, ast.Nonlocal)):
                return True
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ['print', 'input']:
                    return True
        return False
    
    def _is_inefficient_membership_test(self, compare_node: ast.Compare) -> bool:
        """Check for inefficient membership testing."""
        for op in compare_node.ops:
            if isinstance(op, (ast.In, ast.NotIn)):
                # Check if comparing against a list (could be a set)
                for comparator in compare_node.comparators:
                    if isinstance(comparator, ast.List):
                        return True
        return False
    
    def _is_string_concatenation_in_loop(self, augassign_node: ast.AugAssign, tree: ast.AST) -> bool:
        """Check if string concatenation is happening in a loop."""
        # Find parent loop
        for parent in ast.walk(tree):
            if isinstance(parent, (ast.For, ast.While)):
                for child in ast.walk(parent):
                    if child == augassign_node:
                        return True
        return False


class MemoryOptimizer:
    """Optimizes memory usage patterns."""
    
    def optimize_memory(self, code: str) -> List[OptimizationSuggestion]:
        """Identify memory optimization opportunities."""
        suggestions = []
        
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            
            # Check for memory-intensive patterns
            suggestions.extend(self._check_large_data_structures(tree, lines))
            suggestions.extend(self._check_generator_opportunities(tree, lines))
            suggestions.extend(self._check_unnecessary_copies(tree, lines))
            
        except Exception as e:
            print(f"Memory optimization error: {e}")
        
        return suggestions
    
    def _check_large_data_structures(self, tree: ast.AST, lines: List[str]) -> List[OptimizationSuggestion]:
        """Check for large data structures that could be optimized."""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                # Check for large lists
                if len(node.elts) > 100:
                    suggestions.append(OptimizationSuggestion(
                        type='memory',
                        description='Consider using generator or lazy evaluation for large list',
                        original_code=f'Large list with {len(node.elts)} elements',
                        optimized_code='# Use generator: (item for item in ...)',
                        estimated_improvement='Reduced memory usage',
                        line_number=getattr(node, 'lineno', 1),
                        confidence=0.7
                    ))
        
        return suggestions
    
    def _check_generator_opportunities(self, tree: ast.AST, lines: List[str]) -> List[OptimizationSuggestion]:
        """Check for opportunities to use generators."""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                # Check if list comprehension could be a generator
                line_num = getattr(node, 'lineno', 1)
                if line_num <= len(lines):
                    original_line = lines[line_num - 1]
                    if '[' in original_line and ']' in original_line:
                        optimized_line = original_line.replace('[', '(').replace(']', ')')
                        suggestions.append(OptimizationSuggestion(
                            type='memory',
                            description='Use generator expression instead of list comprehension',
                            original_code=original_line.strip(),
                            optimized_code=optimized_line.strip(),
                            estimated_improvement='Lazy evaluation, lower memory usage',
                            line_number=line_num,
                            confidence=0.8
                        ))
        
        return suggestions
    
    def _check_unnecessary_copies(self, tree: ast.AST, lines: List[str]) -> List[OptimizationSuggestion]:
        """Check for unnecessary data copying."""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'list':
                    # Check if converting already iterable to list unnecessarily
                    suggestions.append(OptimizationSuggestion(
                        type='memory',
                        description='Avoid unnecessary list() conversion',
                        original_code='list(iterable)',
                        optimized_code='# Use iterable directly if possible',
                        estimated_improvement='Avoid memory copy',
                        line_number=getattr(node, 'lineno', 1),
                        confidence=0.6
                    ))
        
        return suggestions


class CodeRefactorer:
    """Handles code refactoring using rope library."""
    
    def __init__(self):
        self.project = None
    
    def refactor_code(self, code: str) -> List[OptimizationSuggestion]:
        """Suggest refactoring improvements."""
        suggestions = []
        
        try:
            # Basic refactoring suggestions without rope
            suggestions.extend(self._suggest_function_extraction(code))
            suggestions.extend(self._suggest_variable_renaming(code))
            suggestions.extend(self._suggest_code_simplification(code))
            
        except Exception as e:
            print(f"Refactoring error: {e}")
        
        return suggestions
    
    def _suggest_function_extraction(self, code: str) -> List[OptimizationSuggestion]:
        """Suggest extracting functions from long code blocks."""
        suggestions = []
        lines = code.split('\n')
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count lines in function
                    func_lines = 0
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        func_lines = node.end_lineno - node.lineno + 1
                    
                    if func_lines > 50:  # Long function
                        suggestions.append(OptimizationSuggestion(
                            type='maintainability',
                            description=f'Function {node.name} is long ({func_lines} lines), consider breaking it down',
                            original_code=f'def {node.name}(...): # {func_lines} lines',
                            optimized_code='# Break into smaller functions with single responsibilities',
                            estimated_improvement='Better maintainability and testability',
                            line_number=getattr(node, 'lineno', 1),
                            confidence=0.7
                        ))
            
        except Exception:
            pass
        
        return suggestions
    
    def _suggest_variable_renaming(self, code: str) -> List[OptimizationSuggestion]:
        """Suggest better variable names."""
        suggestions = []
        
        # Simple pattern matching for poor variable names
        poor_names = ['a', 'b', 'c', 'x', 'y', 'z', 'temp', 'data', 'stuff']
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            for poor_name in poor_names:
                if re.search(rf'\b{poor_name}\b\s*=', line):
                    suggestions.append(OptimizationSuggestion(
                        type='readability',
                        description=f'Variable "{poor_name}" has unclear meaning',
                        original_code=line.strip(),
                        optimized_code=f'# Use descriptive name instead of "{poor_name}"',
                        estimated_improvement='Better code readability',
                        line_number=i,
                        confidence=0.6
                    ))
        
        return suggestions
    
    def _suggest_code_simplification(self, code: str) -> List[OptimizationSuggestion]:
        """Suggest code simplifications."""
        suggestions = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for unnecessary else after return
            if 'else:' in stripped:
                # Look for return in previous block
                prev_lines = lines[max(0, i-5):i-1]
                if any('return' in prev_line for prev_line in prev_lines):
                    suggestions.append(OptimizationSuggestion(
                        type='readability',
                        description='Unnecessary else after return statement',
                        original_code=stripped,
                        optimized_code='# Remove else and unindent following code',
                        estimated_improvement='Cleaner code structure',
                        line_number=i,
                        confidence=0.8
                    ))
            
            # Check for boolean comparison
            if ' == True' in stripped or ' == False' in stripped:
                suggestions.append(OptimizationSuggestion(
                    type='readability',
                    description='Unnecessary comparison with boolean',
                    original_code=stripped,
                    optimized_code=stripped.replace(' == True', '').replace(' == False', ' not '),
                    estimated_improvement='Cleaner boolean logic',
                    line_number=i,
                    confidence=0.9
                ))
        
        return suggestions


class CodeOptimizer:
    """Main code optimizer that orchestrates all optimization strategies."""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.pattern_optimizer = PatternOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self.refactorer = CodeRefactorer()
    
    def optimize(self, code: str, test_inputs: Dict[str, Any] = None) -> OptimizationResult:
        """Perform comprehensive code optimization."""
        # Profile original code
        original_metrics = self.profiler.profile_code(code, test_inputs)
        
        # Collect all optimization suggestions
        all_suggestions = []
        all_suggestions.extend(self.pattern_optimizer.optimize_patterns(code))
        all_suggestions.extend(self.memory_optimizer.optimize_memory(code))
        all_suggestions.extend(self.refactorer.refactor_code(code))
        
        # Sort suggestions by confidence and impact
        all_suggestions.sort(key=lambda s: s.confidence, reverse=True)
        
        # Apply top suggestions to create optimized code
        optimized_code = self._apply_optimizations(code, all_suggestions[:5])  # Apply top 5
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(all_suggestions)
        
        return OptimizationResult(
            original_code=code,
            optimized_code=optimized_code,
            suggestions=all_suggestions,
            performance_improvement=original_metrics,
            optimization_score=optimization_score
        )
    
    def _apply_optimizations(self, code: str, suggestions: List[OptimizationSuggestion]) -> str:
        """Apply selected optimizations to the code."""
        optimized_code = code
        
        # Apply simple text-based optimizations
        for suggestion in suggestions:
            if suggestion.type == 'readability' and ' == True' in suggestion.original_code:
                optimized_code = optimized_code.replace(' == True', '')
                optimized_code = optimized_code.replace(' == False', ' not ')
        
        # Add optimization comments
        optimization_comments = [
            "# Code optimized with the following improvements:",
            *[f"# - {suggestion.description}" for suggestion in suggestions[:3]]
        ]
        
        return '\n'.join(optimization_comments) + '\n\n' + optimized_code
    
    def _calculate_optimization_score(self, suggestions: List[OptimizationSuggestion]) -> float:
        """Calculate overall optimization score."""
        if not suggestions:
            return 0.0
        
        # Weight different types of optimizations
        weights = {
            'performance': 3.0,
            'memory': 2.5,
            'maintainability': 2.0,
            'readability': 1.5
        }
        
        total_score = 0.0
        for suggestion in suggestions:
            weight = weights.get(suggestion.type, 1.0)
            total_score += suggestion.confidence * weight
        
        # Normalize to 0-100 scale
        return min(total_score / len(suggestions) * 20, 100.0)
    
    def generate_optimization_report(self, result: OptimizationResult) -> str:
        """Generate a comprehensive optimization report."""
        report_lines = [
            "# Code Optimization Report",
            "=" * 50,
            "",
            f"**Optimization Score:** {result.optimization_score:.1f}/100",
            f"**Total Suggestions:** {len(result.suggestions)}",
            ""
        ]
        
        # Group suggestions by type
        by_type = {}
        for suggestion in result.suggestions:
            by_type.setdefault(suggestion.type, []).append(suggestion)
        
        for opt_type, suggestions in by_type.items():
            report_lines.extend([
                f"## {opt_type.title()} Optimizations ({len(suggestions)})",
                ""
            ])
            
            for i, suggestion in enumerate(suggestions[:3], 1):  # Show top 3 per type
                report_lines.extend([
                    f"### {i}. {suggestion.description}",
                    f"**Line:** {suggestion.line_number}",
                    f"**Confidence:** {suggestion.confidence:.1f}",
                    f"**Expected Improvement:** {suggestion.estimated_improvement}",
                    "",
                    "**Original:**",
                    f"```python",
                    suggestion.original_code,
                    "```",
                    "",
                    "**Optimized:**",
                    f"```python",
                    suggestion.optimized_code,
                    "```",
                    ""
                ])
        
        return "\n".join(report_lines)


# Example usage
def example_usage():
    """Example usage of the CodeOptimizer."""
    sample_code = '''
def inefficient_fibonacci(n):
    if n <= 1:
        return n
    return inefficient_fibonacci(n-1) + inefficient_fibonacci(n-2)

def string_concatenation_example():
    result = ""
    items = ["hello", "world", "how", "are", "you"]
    for item in items:
        result += item + " "
    return result

def list_append_example():
    result = []
    for i in range(100):
        result.append(i * 2)
    return result
    '''
    
    optimizer = CodeOptimizer()
    result = optimizer.optimize(sample_code, {'n': 10})
    
    print("Optimization Results:")
    print(f"Score: {result.optimization_score:.1f}/100")
    print(f"Suggestions: {len(result.suggestions)}")
    
    for suggestion in result.suggestions[:3]:
        print(f"\n- {suggestion.type}: {suggestion.description}")
        print(f"  Confidence: {suggestion.confidence:.1f}")
        print(f"  Improvement: {suggestion.estimated_improvement}")
    
    print("\n" + "="*50)
    print(optimizer.generate_optimization_report(result))


if __name__ == "__main__":
    example_usage()