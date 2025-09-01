-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table for projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- e.g., 'pending', 'paid', 'error', 'calculating', 'completed'
    cost_usd NUMERIC(10, 2),
    project_name VARCHAR(255),
    location_lat NUMERIC(9, 6),
    location_lon NUMERIC(9, 6),
    -- lidar_geom GEOMETRY(Point, 4326) -- Example for point cloud, adjust as needed for mesh
    -- For storing a mesh or complex geometry, consider GEOMETRY(Polygon, 4326) or GEOMETRY(MultiPolygon, 4326)
    -- or even a separate table for LIDAR data if it's very large and complex.
    -- For now, let's keep it simple and assume a bounding box or a representative point for lidar_geom
    lidar_geom GEOMETRY(Point, 4326), -- Placeholder, will need refinement based on actual LIDAR data structure
    -- Add other project metadata as needed
    metadata JSONB DEFAULT '{}'
);

-- Table for calculation results
CREATE TABLE IF NOT EXISTS calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    annual_kwh NUMERIC(10, 2),
    shading_loss_pct NUMERIC(5, 2),
    financial_data JSONB,
    -- Add other calculation results as needed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_calculations_project_id ON calculations(project_id);
