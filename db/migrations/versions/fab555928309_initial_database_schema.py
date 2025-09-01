"""Initial database schema

Revision ID: fab555928309
Revises: 
Create Date: 2025-09-01 09:40:56.714103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fab555928309'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text("""
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";

-- Table for projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- e.g., 'pending', 'paid', 'error', 'calculating', 'completed'
    cost_usd NUMERIC(10, 2),
    project_name VARCHAR(255),
    location_lat NUMERIC(9, 6),
    location_lon NUMERIC(9, 6),
    lidar_geom GEOMETRY(Point, 4326), -- Placeholder, will need refinement based on actual LIDAR data structure
    metadata JSONB DEFAULT '{}'
);

-- Table for calculation results
CREATE TABLE IF NOT EXISTS calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    annual_kwh NUMERIC(10, 2),
    shading_loss_pct NUMERIC(5, 2),
    financial_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_calculations_project_id ON calculations(project_id);
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text("DROP TABLE IF EXISTS calculations;"))
    op.execute(sa.text("DROP TABLE IF EXISTS projects;"))
    op.execute(sa.text("DROP EXTENSION IF EXISTS \"uuid-ossp\";"))
    op.execute(sa.text("DROP EXTENSION IF EXISTS postgis;"))