# Calculation Service Coding Plan

This file outlines the development plan for the Calculation Service.

## Phase 1: LIDAR Data Ingestion and Storage

*   **Objective:** Successfully parse and store LIDAR data in the database.
*   **Tasks:**
    *   Implement a function to read `.las` or `.laz` files using `laspy` or `PDAL`.
    *   Convert the raw LIDAR point cloud into a suitable format for PostGIS (e.g., `GEOMETRY` type).
    *   Develop database schema extensions for storing LIDAR data within the `projects` table.
    *   Implement the data persistence logic for LIDAR data via the `/api/calculate` endpoint.

## Phase 2: Core Solar Modeling

*   **Objective:** Integrate PVLib and perform initial solar simulations.
*   **Tasks:**
    *   Set up `PVLib Python` environment and basic usage.
    *   Develop functions to create a 3D representation of the terrain from the stored LIDAR data.
    *   Implement the calculation of annual energy yield, considering terrain and panel specifications.
    *   Integrate weather data (placeholder or external source) into the simulation.
    *   Store the primary calculation results in the `calculations` table.

## Phase 3: Advanced Modeling and Optimization

*   **Objective:** Enhance the accuracy and utility of the solar simulations.
*   **Tasks:**
    *   Implement detailed shading analysis based on the 3D terrain model and panel placement.
    *   Explore and integrate algorithms for optimizing panel placement and orientation for maximum energy yield.
    *   Refine financial modeling aspects based on energy output.
    *   Optimize performance for large-scale LIDAR datasets and complex simulations.

## Phase 4: API and Integration

*   **Objective:** Expose the calculation functionality via a robust API and ensure seamless integration.
*   **Tasks:**
    *   Finalize the `POST /api/calculate` endpoint, handling request body parsing and response formatting.
    *   Ensure proper error handling and logging for all API interactions and internal processes.
    *   Integrate with the database for both input data retrieval and result persistence.
