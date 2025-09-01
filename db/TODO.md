# Database TODO List

This file tracks specific tasks for the PostgreSQL/PostGIS database.

## Schema Refinement

*   **LIDAR Data Storage:** Refine the `lidar_geom` data type in the `projects` table based on the actual structure and size of LIDAR data. Consider if a separate table or a more complex PostGIS type is needed for detailed LIDAR point clouds or meshes.
*   **Additional Tables:** Identify and create any additional tables required for future features (e.g., user management, detailed panel configurations, weather data storage).
*   **Indexing:** Continuously review and optimize indexes for query performance as the application evolves and data grows.

## Database Operations & Management

*   **Connection Pooling:** Implement robust database connection pooling for all microservices interacting with the database to optimize resource usage and performance.
*   **Backup and Restore:** Establish a clear strategy and automated processes for database backups and restores.
*   **Monitoring:** Set up comprehensive monitoring for database performance, health, and resource utilization.
*   **Security:** Implement and enforce strong database security measures (e.g., least privilege, encryption at rest and in transit).

## Migrations

*   Ensure all future schema changes are managed through Alembic migrations.
*   Develop a clear process for creating, reviewing, and applying migrations in development, staging, and production environments.
