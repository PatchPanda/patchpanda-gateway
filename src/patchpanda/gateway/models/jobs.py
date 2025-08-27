"""Job data models."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class JobStatus(str, Enum):
    """Job status values."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class JobType(str, Enum):
    """Job type values."""
    TEST_GENERATION = "test_generation"
    COVERAGE_ANALYSIS = "coverage_analysis"
    TEST_EXECUTION = "test_execution"


class JobPriority(str, Enum):
    """Job priority values."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class JobCreate(BaseModel):
    """Request model for creating a new job."""

    project_id: str = Field(description="Project identifier")
    repository: str = Field(description="Repository name")
    owner: str = Field(description="Repository owner")
    commit_sha: str = Field(description="Commit SHA to analyze")
    branch: str = Field(description="Branch name")

    job_type: JobType = Field(description="Type of job to create")
    priority: JobPriority = Field(default=JobPriority.NORMAL, description="Job priority")

    # Configuration
    config: Optional[Dict[str, Any]] = Field(default=None, description="Job-specific configuration")

    # Metadata
    source: Optional[str] = Field(default="webhook", description="Source of the job")
    user_id: Optional[str] = Field(default=None, description="User who triggered the job")

    model_config = ConfigDict(extra="forbid")


class JobData(BaseModel):
    """Complete job data."""

    id: str = Field(description="Job ID")
    project_id: str = Field(description="Project identifier")
    repository: str = Field(description="Repository name")
    owner: str = Field(description="Repository owner")
    commit_sha: str = Field(description="Commit SHA to analyze")
    branch: str = Field(description="Branch name")

    job_type: JobType = Field(description="Type of job")
    status: JobStatus = Field(description="Current job status")
    priority: JobPriority = Field(description="Job priority")

    # Configuration
    config: Optional[Dict[str, Any]] = Field(default=None, description="Job-specific configuration")

    # Progress tracking
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Job progress percentage")
    current_step: Optional[str] = Field(default=None, description="Current step description")

    # Timing
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When job was created")
    started_at: Optional[datetime] = Field(default=None, description="When job started running")
    completed_at: Optional[datetime] = Field(default=None, description="When job completed")

    # Results
    result: Optional[Dict[str, Any]] = Field(default=None, description="Job results")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")

    # Metadata
    source: str = Field(description="Source of the job")
    user_id: Optional[str] = Field(default=None, description="User who triggered the job")
    worker_id: Optional[str] = Field(default=None, description="Worker that processed the job")

    # Queue information
    queue_position: Optional[int] = Field(default=None, description="Position in queue")
    estimated_start: Optional[datetime] = Field(default=None, description="Estimated start time")

    model_config = ConfigDict(
        ser_json_datetime=lambda v: v.isoformat()
    )


class JobSummary(BaseModel):
    """Summary of job data for listing."""

    id: str = Field(description="Job ID")
    project_id: str = Field(description="Project identifier")
    repository: str = Field(description="Repository name")
    owner: str = Field(description="Repository owner")
    commit_sha: str = Field(description="Commit SHA")
    branch: str = Field(description="Branch name")

    job_type: JobType = Field(description="Type of job")
    status: JobStatus = Field(description="Current job status")
    priority: JobPriority = Field(description="Job priority")

    progress: float = Field(description="Job progress percentage")
    created_at: datetime = Field(description="When job was created")
    completed_at: Optional[datetime] = Field(default=None, description="When job completed")

    source: str = Field(description="Source of the job")
    user_id: Optional[str] = Field(default=None, description="User who triggered the job")

    model_config = ConfigDict(
        ser_json_datetime=lambda v: v.isoformat()
    )
