"""
Streamlit Web Interface for Python Code Generator

A beautiful, interactive web application for generating, validating, testing, and optimizing Python code.
"""

import streamlit as st
import sys
import os
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Handle plotly imports with fallback
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly not available. Charts will be disabled. Install with: `pip install plotly`")

# Add src and parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Import our modules
try:
    from src.code_generator import CodeGenerator, CodeGenerationRequest
    from src.code_validator import CodeValidator
    from src.test_generator import TestGenerator
    from src.code_optimizer import CodeOptimizer
    from config.settings import settings
    from examples.sample_prompts import ALL_PROMPTS, get_prompts_by_category, ADVANCED_PROMPTS
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Streamlit page configuration
st.set_page_config(
    page_title="🤖 AI Python Code Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e4e8;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = ""
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'test_results' not in st.session_state:
        st.session_state.test_results = None
    if 'optimization_results' not in st.session_state:
        st.session_state.optimization_results = None
    if 'generation_history' not in st.session_state:
        st.session_state.generation_history = []


def create_metrics_dashboard(validation_results, test_results, optimization_results):
    """Create a metrics dashboard with key performance indicators."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if validation_results:
            st.metric(
                "Pylint Score", 
                f"{validation_results.pylint_score:.1f}/10",
                delta=f"{validation_results.pylint_score - 5.0:.1f}" if validation_results.pylint_score > 5.0 else None
            )
        else:
            st.metric("Pylint Score", "N/A")
    
    with col2:
        if validation_results:
            complexity = validation_results.complexity_score
            st.metric(
                "Complexity", 
                f"{complexity:.1f}",
                delta="Good" if complexity <= 10 else "High",
                delta_color="normal" if complexity <= 10 else "inverse"
            )
        else:
            st.metric("Complexity", "N/A")
    
    with col3:
        if test_results:
            total_tests = sum(result['execution_result'].total for result in test_results.values())
            total_passed = sum(result['execution_result'].passed for result in test_results.values())
            success_rate = (total_passed / max(total_tests, 1)) * 100
            st.metric(
                "Test Success", 
                f"{success_rate:.1f}%",
                delta=f"{total_passed}/{total_tests} passed"
            )
        else:
            st.metric("Test Success", "N/A")
    
    with col4:
        if optimization_results:
            opt_score = optimization_results.optimization_score
            st.metric(
                "Optimization", 
                f"{opt_score:.1f}/100",
                delta="Good" if opt_score > 70 else "Needs Work",
                delta_color="normal" if opt_score > 70 else "inverse"
            )
        else:
            st.metric("Optimization", "N/A")


def create_quality_chart(validation_results):
    """Create a radar chart showing code quality metrics."""
    if not validation_results or not PLOTLY_AVAILABLE:
        return None
    
    categories = ['Style', 'Security', 'Complexity', 'Maintainability', 'Documentation']
    
    # Calculate scores (0-100 scale)
    style_score = max(0, 100 - len(validation_results.style_issues) * 10)
    security_score = max(0, 100 - len(validation_results.security_issues) * 20)
    complexity_score = max(0, 100 - validation_results.complexity_score * 5)
    maintainability_score = min(100, validation_results.maintainability_index)
    doc_score = 80 if len(validation_results.suggestions) < 3 else 60
    
    values = [style_score, security_score, complexity_score, maintainability_score, doc_score]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Code Quality'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="Code Quality Radar Chart"
    )
    
    return fig


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Python Code Generator</h1>', unsafe_allow_html=True)
    st.markdown("Generate • Validate • Test • Optimize Python Code with AI", unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # LLM Provider selection
        provider = st.selectbox(
            "LLM Provider",
            ["openai", "anthropic"],
            help="Choose your preferred LLM provider"
        )
        
        # API Key input
        if provider == "openai":
            api_key = st.text_input(
                "OpenAI API Key", 
                type="password",
                help="Enter your OpenAI API key"
            )
        else:
            api_key = st.text_input(
                "Anthropic API Key", 
                type="password",
                help="Enter your Anthropic API key"
            )
        
        st.divider()
        
        # Settings
        st.header("🎛️ Settings")
        temperature = st.slider("Temperature", 0.0, 2.0, 0.2, 0.1)
        max_tokens = st.slider("Max Tokens", 500, 4000, 2000, 100)
        
        # Quick examples
        st.header("📚 Quick Examples")
        if st.button("Fibonacci Function"):
            st.session_state.prompt_input = "Create a function to calculate fibonacci numbers"
        if st.button("Binary Search"):
            st.session_state.prompt_input = "Implement binary search algorithm"
        if st.button("Data Structure"):
            st.session_state.prompt_input = "Create a binary tree class with insert and search methods"
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Generate", "📊 Dashboard", "📈 Analysis", "📋 History"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Code Generation</h2>', unsafe_allow_html=True)
        
        # Code generation form
        with st.form("code_generation_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                prompt = st.text_area(
                    "Describe the code you want to generate:",
                    height=150,
                    placeholder="e.g., Create a function to sort a list using quicksort algorithm",
                    key="prompt_input"
                )
            
            with col2:
                st.write("**Advanced Options:**")
                function_name = st.text_input("Function Name (optional)")
                return_type = st.text_input("Return Type (optional)")
                requirements = st.text_area("Additional Requirements", height=80)
            
            # Form buttons must be inside the form
            col1, col2, col3 = st.columns(3)
            with col1:
                generate_button = st.form_submit_button("🚀 Generate Code", type="primary")
            with col2:
                validate_button = st.form_submit_button("🔍 Validate Only")
            with col3:
                full_pipeline_button = st.form_submit_button("⚡ Full Pipeline")
        
        # Process generation request
        if generate_button or validate_button or full_pipeline_button:
            if not prompt.strip():
                st.error("Please provide a code description!")
                st.stop()
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Generate code (if not validate only)
                if not validate_button:
                    status_text.text("🤖 Generating code with AI...")
                    progress_bar.progress(20)
                    
                    if not api_key:
                        st.warning("⚠️ No API key provided. Using sample code for demonstration.")
                        # Use a sample code for demo purposes
                        sample_code = f'''
def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
                        st.session_state.generated_code = sample_code
                    else:
                        # Use actual LLM generation
                        generator = CodeGenerator(provider)
                        request = CodeGenerationRequest(
                            description=prompt,
                            function_name=function_name if function_name else None,
                            return_type=return_type if return_type else None,
                            additional_requirements=requirements if requirements else None
                        )
                        result = generator.generate(request)
                        st.session_state.generated_code = result.code
                else:
                    # Use existing code or sample
                    if not st.session_state.generated_code:
                        st.session_state.generated_code = '''
def sample_function():
    """Sample function for validation."""
    return "Hello, World!"
'''
                
                progress_bar.progress(40)
                
                # Step 2: Validate code
                status_text.text("🔍 Validating code quality...")
                validator = CodeValidator()
                st.session_state.validation_results = validator.validate(st.session_state.generated_code)
                progress_bar.progress(60)
                
                if full_pipeline_button:
                    # Step 3: Generate tests
                    status_text.text("🧪 Generating and running tests...")
                    test_generator = TestGenerator()
                    st.session_state.test_results = test_generator.generate_and_run_tests(
                        st.session_state.generated_code
                    )
                    progress_bar.progress(80)
                    
                    # Step 4: Optimize code
                    status_text.text("⚡ Analyzing optimization opportunities...")
                    optimizer = CodeOptimizer()
                    st.session_state.optimization_results = optimizer.optimize(
                        st.session_state.generated_code
                    )
                
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                
                # Add to history
                st.session_state.generation_history.append({
                    'timestamp': time.time(),
                    'prompt': prompt,
                    'code': st.session_state.generated_code,
                    'validation': st.session_state.validation_results,
                    'full_pipeline': full_pipeline_button
                })
                
                time.sleep(1)  # Brief pause to show completion
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                progress_bar.empty()
                status_text.empty()
        
        # Display generated code
        if st.session_state.generated_code:
            st.markdown("### 📝 Generated Code")
            st.code(st.session_state.generated_code, language="python")
            
            # Download button
            st.download_button(
                "📥 Download Code",
                st.session_state.generated_code,
                file_name="generated_code.py",
                mime="text/plain"
            )
    
    with tab2:
        st.markdown('<h2 class="sub-header">Quality Dashboard</h2>', unsafe_allow_html=True)
        
        if st.session_state.validation_results or st.session_state.test_results or st.session_state.optimization_results:
            # Metrics dashboard
            create_metrics_dashboard(
                st.session_state.validation_results,
                st.session_state.test_results,
                st.session_state.optimization_results
            )
            
            st.divider()
            
            # Quality visualization
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.validation_results:
                    fig = create_quality_chart(st.session_state.validation_results)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    elif not PLOTLY_AVAILABLE:
                        # Fallback: text-based quality metrics
                        st.subheader("Code Quality Metrics")
                        val = st.session_state.validation_results
                        st.write(f"• **Style Score**: {max(0, 100 - len(val.style_issues) * 10)}/100")
                        st.write(f"• **Security Score**: {max(0, 100 - len(val.security_issues) * 20)}/100")
                        st.write(f"• **Complexity**: {val.complexity_score}")
                        st.write(f"• **Maintainability**: {val.maintainability_index}")
                        st.write(f"• **Documentation**: {'Good' if len(val.suggestions) < 3 else 'Needs Work'}")
            
            with col2:
                if st.session_state.optimization_results:
                    # Optimization suggestions chart
                    suggestions = st.session_state.optimization_results.suggestions
                    if suggestions and PLOTLY_AVAILABLE:
                        suggestion_types = {}
                        for suggestion in suggestions:
                            suggestion_types[suggestion.type] = suggestion_types.get(suggestion.type, 0) + 1
                        
                        fig = px.pie(
                            values=list(suggestion_types.values()),
                            names=list(suggestion_types.keys()),
                            title="Optimization Suggestions by Type"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    elif suggestions and not PLOTLY_AVAILABLE:
                        # Fallback: simple text-based chart
                        suggestion_types = {}
                        for suggestion in suggestions:
                            suggestion_types[suggestion.type] = suggestion_types.get(suggestion.type, 0) + 1
                        
                        st.subheader("Optimization Suggestions by Type")
                        for stype, count in suggestion_types.items():
                            st.write(f"• **{stype}**: {count} suggestions")
        else:
            st.info("🔍 Generate code first to see the quality dashboard!")
    
    with tab3:
        st.markdown('<h2 class="sub-header">Detailed Analysis</h2>', unsafe_allow_html=True)
        
        if st.session_state.validation_results:
            # Validation results
            st.subheader("🔍 Code Validation Results")
            
            val_results = st.session_state.validation_results
            
            if len(val_results.syntax_errors) == 0:
                st.success("✅ No syntax errors found!")
            else:
                st.error(f"❌ Found {len(val_results.syntax_errors)} syntax errors:")
                for error in val_results.syntax_errors:
                    st.error(f"• {error}")
            
            if val_results.style_issues:
                with st.expander(f"⚠️ Style Issues ({len(val_results.style_issues)})"):
                    for issue in val_results.style_issues:
                        st.warning(f"• {issue}")
            
            if val_results.suggestions:
                with st.expander(f"💡 Improvement Suggestions ({len(val_results.suggestions)})"):
                    for suggestion in val_results.suggestions:
                        st.info(f"• {suggestion}")
        
        if st.session_state.test_results:
            # Test results
            st.subheader("🧪 Test Results")
            
            for func_name, result in st.session_state.test_results.items():
                exec_result = result['execution_result']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(f"{func_name} - Passed", exec_result.passed)
                with col2:
                    st.metric(f"{func_name} - Failed", exec_result.failed)
                with col3:
                    st.metric(f"{func_name} - Success Rate", f"{(exec_result.passed/max(exec_result.total, 1)*100):.1f}%")
                
                if exec_result.failures:
                    with st.expander(f"View {func_name} Test Failures"):
                        for failure in exec_result.failures:
                            st.error(f"• {failure}")
        
        if st.session_state.optimization_results:
            # Optimization results
            st.subheader("⚡ Optimization Analysis")
            
            opt_results = st.session_state.optimization_results
            
            st.metric("Overall Optimization Score", f"{opt_results.optimization_score:.1f}/100")
            
            if opt_results.suggestions:
                st.subheader("🔧 Optimization Suggestions")
                
                for i, suggestion in enumerate(opt_results.suggestions[:10], 1):  # Show top 10
                    with st.expander(f"{i}. {suggestion.type.title()}: {suggestion.description}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Original Code:**")
                            st.code(suggestion.original_code, language="python")
                        with col2:
                            st.write("**Suggested Improvement:**")
                            st.code(suggestion.optimized_code, language="python")
                        
                        st.write(f"**Confidence:** {suggestion.confidence:.1f}")
                        st.write(f"**Expected Improvement:** {suggestion.estimated_improvement}")
    
    with tab4:
        st.markdown('<h2 class="sub-header">Generation History</h2>', unsafe_allow_html=True)
        
        if st.session_state.generation_history:
            for i, entry in enumerate(reversed(st.session_state.generation_history), 1):
                with st.expander(f"#{i} - {time.strftime('%H:%M:%S', time.localtime(entry['timestamp']))} - {entry['prompt'][:50]}..."):
                    st.write(f"**Prompt:** {entry['prompt']}")
                    st.code(entry['code'], language="python")
                    
                    if entry['validation']:
                        val = entry['validation']
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Pylint Score", f"{val.pylint_score:.1f}/10")
                        with col2:
                            st.metric("Complexity", f"{val.complexity_score:.1f}")
                        with col3:
                            st.metric("Issues", len(val.syntax_errors) + len(val.style_issues))
            
            if st.button("🗑️ Clear History"):
                st.session_state.generation_history = []
                st.rerun()
        else:
            st.info("📝 No generation history yet. Generate some code to see it here!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        🤖 AI Python Code Generator | Built with Streamlit | 
        <a href="https://github.com" target="_blank">View on GitHub</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()