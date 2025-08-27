"""Initial migration

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=100), nullable=False),
        sa.Column('repository', sa.String(length=200), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('commit_sha', sa.String(length=40), nullable=False),
        sa.Column('branch', sa.String(length=100), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('current_step', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('worker_id', sa.String(length=100), nullable=True),
        sa.Column('queue_position', sa.Integer(), nullable=True),
        sa.Column('estimated_start', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_project_id'), 'jobs', ['project_id'], unique=False)

    # Create coverage table
    op.create_table('coverage',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=100), nullable=False),
        sa.Column('repository', sa.String(length=200), nullable=False),
        sa.Column('commit_sha', sa.String(length=40), nullable=False),
        sa.Column('branch', sa.String(length=100), nullable=False),
        sa.Column('overall_coverage', sa.Float(), nullable=False),
        sa.Column('total_files', sa.Integer(), nullable=False),
        sa.Column('covered_files', sa.Integer(), nullable=False),
        sa.Column('files', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('test_framework', sa.String(length=100), nullable=True),
        sa.Column('coverage_tool', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coverage_job_id'), 'coverage', ['job_id'], unique=False)
    op.create_index(op.f('ix_coverage_project_id'), 'coverage', ['project_id'], unique=False)

    # Create billing_projects table
    op.create_table('billing_projects',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=False),
        sa.Column('monthly_limit', sa.Integer(), nullable=True),
        sa.Column('current_usage', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('key_prefix', sa.String(length=10), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['billing_projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create repository_bindings table
    op.create_table('repository_bindings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('repository', sa.String(length=200), nullable=False),
        sa.Column('installation_id', sa.Integer(), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['billing_projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create audit_events table
    op.create_table('audit_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('project_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('repository_bindings')
    op.drop_table('api_keys')
    op.drop_table('billing_projects')
    op.drop_index(op.f('ix_coverage_project_id'), table_name='coverage')
    op.drop_index(op.f('ix_coverage_job_id'), table_name='coverage')
    op.drop_table('coverage')
    op.drop_index(op.f('ix_jobs_project_id'), table_name='jobs')
    op.drop_table('jobs')
