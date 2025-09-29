import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Configuration settings for the code generation project."""
    
    # LLM API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    DEFAULT_MODEL: str = "gpt-4"
    
    # Code Generation Settings
    MAX_CODE_LENGTH: int = 5000
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 2000
    
    # Code Quality Thresholds
    MIN_PYLINT_SCORE: float = 8.0
    MAX_COMPLEXITY: int = 10
    MIN_TEST_COVERAGE: float = 80.0
    
    # File Paths
    GENERATED_CODE_DIR: str = "examples/generated_code"
    TEST_OUTPUT_DIR: str = "test_results"
    
    # Validation Settings
    ENABLE_PEP8_CHECK: bool = True
    ENABLE_TYPE_CHECK: bool = True
    ENABLE_SECURITY_CHECK: bool = True
    
    # Optimization Settings
    ENABLE_PERFORMANCE_OPTIMIZATION: bool = True
    ENABLE_MEMORY_OPTIMIZATION: bool = True
    ENABLE_REFACTORING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()