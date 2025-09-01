# Calculation Service TODO List

This file tracks specific tasks for the Calculation Service.

## Core Logic Implementation

*   **LIDAR Data Processing:**
    *   Implement parsing of `.las` or `.laz` files (using `laspy` or `PDAL`).
    *   Convert LIDAR point cloud data into a 3D terrain model (mesh or point cloud).
    *   Store the processed LIDAR data efficiently in the PostGIS database.
*   **Solar Modeling:**
    *   Integrate `PVLib Python` for high-fidelity solar simulation.
    *   Develop algorithms to calculate annual energy yield based on the 3D terrain model and weather data.
    *   Implement shading loss calculations.
    *   Explore optimal panel placement and orientation algorithms.
*   **Database Interaction:**
    *   Persist calculation results (annual kWh, shading loss, financial data) to the `calculations` table.
    *   Ensure efficient retrieval of project and LIDAR data from the `projects` table.

## API Endpoint

*   Implement the `POST /api/calculate` endpoint:
    *   Receive `project_name`, `location`, `lidar_data` (base64 encoded), `panel_specs`, `ground_mount_config`.
    *   Trigger the LIDAR processing and solar modeling.
    *   Return a `project_id` and a status indicating calculation has started.

## Performance & Scalability

*   Optimize LIDAR processing for large datasets.
*   Consider asynchronous processing for long-running calculations.
*   Implement caching strategies for frequently accessed data.

## Testing

*   Develop comprehensive unit tests for LIDAR processing and solar modeling algorithms.
*   Create integration tests for the `/api/calculate` endpoint.

## Future Enhancements

*   Integrate with external weather data APIs.
*   Add support for different panel types and inverter models.
*   Implement more advanced financial modeling.
