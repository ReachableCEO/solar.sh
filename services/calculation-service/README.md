# Calculation Service

This service is responsible for performing the solar calculations. It receives a request with project data, including LIDAR data, and returns a project ID. The calculation is then performed asynchronously.

## API

*   **POST /api/calculate:** Starts a new calculation.
