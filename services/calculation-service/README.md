# Calculation Service

This service is responsible for performing complex solar calculations, including LIDAR data processing and solar modeling. It receives project data, processes it, and stores the results in the database.

## API Endpoints

*   **POST /api/calculate:** Initiates a new solar calculation.
    *   **Request Body (Example):**
        ```json
        {
            "project_name": "Ground Mount Project 1",
            "location": { "lat": 35.79, "lon": -78.78 },
            "lidar_data": "<base64_encoded_lidar_file>",
            "panel_specs": { "type": "mono", "power": 300 },
            "ground_mount_config": { "tilt": 30, "azimuth": 180 }
        }
        ```
    *   **Response:** `{"project_id": "unique_id", "status": "completed", "annual_kwh": 12345.67}` (or "processing" if asynchronous)

*   **GET /health:** A basic health check endpoint that also verifies database connectivity.
    *   **Response:** `"OK"` (200) on success, or an error message (500) on failure.

## Environment Variables

This service requires the following environment variable to be set:

*   `DATABASE_URL`: The connection string for your PostgreSQL database. Example: `postgresql://user:password@host:5432/database_name`.

It is recommended to use a `.env` file for local development.

## Running the Service

### Prerequisites

*   Python 3.9+
*   `pip`
*   Docker (optional, for containerized deployment)

### Local Development

1.  **Navigate to the service directory:**
    ```bash
    cd services/calculation-service
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file:**
    ```
    DATABASE_URL=postgresql://user:password@localhost:5432/solcalc_db
    ```
    *Replace with your actual values.*

4.  **Run the application:**
    ```bash
    python app.py
    ```
    The service will run on `http://0.0.0.0:5001`.

### Docker

This service is part of a larger microservices architecture managed by `docker-compose.yml` at the project root. To run the entire stack:

1.  **Navigate to the project root directory:**
    ```bash
    cd ../..
    ```
2.  **Bring up the Docker Compose stack:**
    ```bash
    docker compose up -d --build
    ```
    *Ensure your `.env` file at the project root is correctly configured as described above.*

Alternatively, to run only this service with Docker (for isolated testing/development):

1.  **Navigate to the service directory:**
    ```bash
    cd services/calculation-service
    ```
2.  **Build the Docker image:**
    ```bash
    docker build -t calculation-service .
    ```
3.  **Run the Docker container:**
    ```bash
    docker run -p 5001:5001 --env-file .env calculation-service
    ```
    *Ensure your `.env` file is correctly configured as described above.*

## Testing

To run the unit tests for this service:

1.  **Navigate to the service directory:**
    ```bash
    cd services/calculation-service
    ```
2.  **Run tests:**
    ```bash
    python -m unittest tests/test_app.py
    ```