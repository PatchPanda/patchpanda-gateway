"""Database table definitions."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class Job(Base):
    """Job table for storing test generation job metadata."""

    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(100), nullable=False, index=True)
    repository = Column(String(200), nullable=False)
    owner = Column(String(100), nullable=False)
    commit_sha = Column(String(40), nullable=False)
    branch = Column(String(100), nullable=False)

    job_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    priority = Column(String(20), nullable=False, default="normal")

    config = Column(JSON, nullable=True)
    progress = Column(Float, nullable=False, default=0.0)
    current_step = Column(String(200), nullable=True)

    created_at = Column(DateTime, nullable=False, default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    source = Column(String(50), nullable=False, default="webhook")
    user_id = Column(String(100), nullable=True)
    worker_id = Column(String(100), nullable=True)

    queue_position = Column(Integer, nullable=True)
    estimated_start = Column(DateTime, nullable=True)


class Coverage(Base):
    """Coverage table for storing test coverage data."""

    __tablename__ = "coverage"

    id = Column(String(36), primary_key=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    project_id = Column(String(100), nullable=False, index=True)
    repository = Column(String(200), nullable=False)
    commit_sha = Column(String(40), nullable=False)
    branch = Column(String(100), nullable=False)

    overall_coverage = Column(Float, nullable=False)
    total_files = Column(Integer, nullable=False)
    covered_files = Column(Integer, nullable=False)

    files = Column(JSON, nullable=True)  # File-level coverage data
    generated_at = Column(DateTime, nullable=False, default=func.now())
    test_framework = Column(String(100), nullable=True)
    coverage_tool = Column(String(100), nullable=True)

    raw_data = Column(JSON, nullable=True)

    # Relationship
    job = relationship("Job", backref="coverage_records")


class BillingProject(Base):
    """Billing projects table."""

    __tablename__ = "billing_projects"

    id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Billing information
    plan = Column(String(50), nullable=False, default="free")
    monthly_limit = Column(Integer, nullable=True)
    current_usage = Column(Integer, nullable=False, default=0)

    # Status
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class ApiKey(Base):
    """API keys table."""

    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("billing_projects.id"), nullable=False)
    name = Column(String(200), nullable=False)

    # Key data (hashed)
    key_hash = Column(String(255), nullable=False)
    key_prefix = Column(String(10), nullable=False)  # First 10 chars for identification

    # Permissions
    permissions = Column(JSON, nullable=True)

    # Status
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    last_used_at = Column(DateTime, nullable=True)

    # Relationship
    project = relationship("BillingProject", backref="api_keys")


class RepositoryBinding(Base):
    """Repository to project bindings table."""

    __tablename__ = "repository_bindings"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("billing_projects.id"), nullable=False)

    # Repository information
    owner = Column(String(100), nullable=False)
    repository = Column(String(200), nullable=False)
    installation_id = Column(Integer, nullable=False)

    # Configuration
    config = Column(JSON, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("BillingProject", backref="repository_bindings")

    # Unique constraint
    __table_args__ = (
        {"sqlite_on_conflict": "REPLACE"},
    )


class AuditEvent(Base):
    """Audit events table."""

    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=func.now())

    # Event information
    event_type = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=True)
    project_id = Column(String(100), nullable=True)

    # Event details
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)

    # Index for efficient querying
    __table_args__ = (
        {"sqlite_on_conflict": "REPLACE"},
    )
