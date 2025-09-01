# Database Coding Plan

This file outlines the development plan for the PostgreSQL/PostGIS database.

## Phase 1: Initial Setup and Schema Definition (Completed)

*   **Objective:** Establish the foundational database infrastructure and initial schema.
*   **Status:** This phase is complete. Key tasks performed:
    *   Created `db/` directory for database-related files.
    *   Defined initial database schema (`projects` and `calculations` tables) in `db/schema.sql`, including PostGIS extensions and UUID generation.
    *   Configured Docker Compose (`docker-compose.yml`) to include a PostgreSQL/PostGIS service, ensuring it initializes with `db/schema.sql`.
    *   Initialized Alembic within the `db/` directory for migration management.
    *   Configured `db/alembic.ini` and `db/migrations/env.py` to connect to the database using environment variables.
    *   Created an initial Alembic migration script (`db/migrations/versions/..._initial_database_schema.py`) containing the DDL from `db/schema.sql`.

## Phase 2: Applying Migrations and Initial Data

*   **Objective:** Apply the initial schema to the database and potentially populate with seed data.
*   **Tasks:**
    *   Run `alembic upgrade head` to apply the initial migration to the database.
    *   Develop scripts or use tools to insert initial seed data if required for development or testing.

## Phase 3: Schema Refinement and Evolution

*   **Objective:** Iteratively refine and extend the database schema as application requirements evolve.
*   **Tasks:**
    *   For each new feature requiring database changes, create new Alembic migration scripts.
    *   Refine the `lidar_geom` data type and storage strategy based on actual LIDAR data characteristics and performance needs.
    *   Add new tables and columns as identified in the `db/TODO.md`.
    *   Optimize existing tables and indexes for performance.

## Phase 4: Advanced Database Management

*   **Objective:** Implement robust database management practices for production readiness.
*   **Tasks:**
    *   Integrate database connection pooling into microservices.
    *   Set up automated backup and restore procedures.
    *   Implement comprehensive database monitoring and alerting.
    *   Strengthen database security measures (e.g., user roles, access control).
