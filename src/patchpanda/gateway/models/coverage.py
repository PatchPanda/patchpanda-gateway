"""Coverage data models."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class FileCoverage(BaseModel):
    """Coverage data for a single file."""

    file_path: str = Field(description="Path to the file")
    total_lines: int = Field(ge=0, description="Total number of lines")
    covered_lines: int = Field(ge=0, description="Number of covered lines")
    uncovered_lines: int = Field(ge=0, description="Number of uncovered lines")
    coverage_percentage: float = Field(ge=0.0, le=100.0, description="Coverage percentage")

    # Detailed coverage information
    line_coverage: Optional[Dict[int, bool]] = Field(default=None, description="Line-by-line coverage")
    branch_coverage: Optional[Dict[str, float]] = Field(default=None, description="Branch coverage data")


class CoverageData(BaseModel):
    """Complete coverage data for a job."""

    id: Optional[str] = Field(default=None, description="Coverage data ID")
    job_id: str = Field(description="Associated job ID")
    project_id: str = Field(description="Project identifier")
    repository: str = Field(description="Repository name")
    commit_sha: str = Field(description="Commit SHA")
    branch: str = Field(description="Branch name")

    # Coverage metrics
    overall_coverage: float = Field(ge=0.0, le=100.0, description="Overall coverage percentage")
    total_files: int = Field(ge=0, description="Total number of files")
    covered_files: int = Field(ge=0, description="Number of files with coverage")

    # File-level coverage
    files: List[FileCoverage] = Field(default_factory=list, description="Coverage data for individual files")

    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When coverage was generated")
    test_framework: Optional[str] = Field(default=None, description="Test framework used")
    coverage_tool: Optional[str] = Field(default=None, description="Coverage tool used")

    # Additional data
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw coverage data from tool")

    model_config = ConfigDict(
        ser_json_datetime=lambda v: v.isoformat()
    )


class CoverageSummary(BaseModel):
    """Summary of coverage data for listing."""

    id: str = Field(description="Coverage data ID")
    job_id: str = Field(description="Associated job ID")
    project_id: str = Field(description="Project identifier")
    repository: str = Field(description="Repository name")
    commit_sha: str = Field(description="Commit SHA")
    branch: str = Field(description="Branch name")

    overall_coverage: float = Field(description="Overall coverage percentage")
    total_files: int = Field(description="Total number of files")
    covered_files: int = Field(description="Number of files with coverage")

    generated_at: datetime = Field(description="When coverage was generated")

    model_config = ConfigDict(
        ser_json_datetime=lambda v: v.isoformat()
    )
