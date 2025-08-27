"""Configuration models for .testbot.yml files."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class TestbotConfig(BaseModel):
    """Configuration for PatchPanda test bot."""

    enabled: bool = Field(default=True, description="Enable/disable the bot")
    test_generation: bool = Field(default=True, description="Enable test generation")
    coverage_analysis: bool = Field(default=True, description="Enable coverage analysis")

    # Test generation settings
    max_tests: int = Field(default=100, ge=1, le=1000, description="Maximum number of tests to generate")
    timeout_minutes: int = Field(default=30, ge=1, le=480, description="Test generation timeout in minutes")

    # File patterns
    include_patterns: Optional[List[str]] = Field(default=None, description="File patterns to include")
    exclude_patterns: Optional[List[str]] = Field(default=None, description="File patterns to exclude")

    # Framework settings
    test_framework: Optional[str] = Field(default=None, description="Test framework to use")
    test_directory: Optional[str] = Field(default="tests", description="Directory for generated tests")

    # Coverage settings
    coverage_threshold: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Minimum coverage threshold")
    coverage_exclude: Optional[List[str]] = Field(default=None, description="Files to exclude from coverage")

    # Advanced settings
    custom_settings: Optional[Dict[str, Any]] = Field(default=None, description="Custom framework-specific settings")

    model_config = ConfigDict(extra="forbid")  # Reject unknown fields
