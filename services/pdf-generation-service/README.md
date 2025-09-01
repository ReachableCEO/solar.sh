# PDF Generation Service

This service is responsible for generating comprehensive PDF reports based on project and calculation data retrieved from the database.

## API Endpoints

*   **GET /api/download/:project_id:** Generates and provides a PDF report for the specified project ID. This endpoint is exposed via the API Gateway, which also handles payment gating.
    *   **Parameters:**
        *   `project_id` (UUID) - The ID of the project for which to generate the report.
        *   `format` (optional) - Report format: 'detailed' (default) or 'summary'
        *   `include_financial` (optional) - Include financial data: 'true' (default) or 'false'
    *   **Response:** A PDF file download.
    *   **Example:** `/api/download/12345678-1234-5678-9012-123456789012?format=summary&include_financial=false`

*   **HEAD /api/download/:project_id:** Check if PDF is available for download without generating it.
    *   **Parameters:** `project_id` (UUID) - The ID of the project to check.
    *   **Response:** 200 if available, 403 if unpaid, 404 if not found.

*   **POST /api/cache/clear/:project_id:** Clear cached PDF for a specific project.
    *   **Parameters:** `project_id` (UUID) - The ID of the project to clear cache for.
    *   **Response:** Success message.

*   **POST /api/cache/clear-all:** Clear all cached PDFs.
    *   **Response:** Success message.

*   **DELETE /api/data/privacy/:project_id:** GDPR: Delete all data related to a project (right to erasure).
    *   **Parameters:** `project_id` (UUID) - The ID of the project to delete data for.
    *   **Response:** Success message.

*   **GET /api/data/export/:project_id:** GDPR: Export all data related to a project (right to data portability).
    *   **Parameters:** `project_id` (UUID) - The ID of the project to export data for.
    *   **Response:** JSON object containing exported project data.

*   **GET /health:** A health check endpoint that verifies database connectivity.
    *   **Response:** JSON with status and service information.

## Dependencies

The service requires the following Python packages (see `requirements.txt`):

*   Flask - Web framework
*   Flask-Caching - Caching functionality
*   Jinja2 - Template engine
*   WeasyPrint - PDF generation
*   psycopg2-binary - PostgreSQL database connector
*   python-dotenv - Environment variable management

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
    cd services/pdf-generation-service
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file:**
    ```
    DATABASE_URL=postgresql://user:password@localhost:5432/solcalc_db
    GENERATION_DATE="September 1, 2025"
    ```
    *Replace with your actual values.*

4.  **Run the application:**
    ```bash
    python app.py
    ```
    The service will run on `http://0.0.0.0:5002`.

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
    cd services/pdf-generation-service
    ```
2.  **Build the Docker image:**
    ```bash
    docker build -t pdf-generation-service .
    ```
3.  **Run the Docker container:**
    ```bash
    docker run -p 5002:5002 --env-file .env pdf-generation-service
    ```
    *Ensure your `.env` file is correctly configured as described above.*

## Testing

To run the unit tests for this service:

1.  **Navigate to the service directory:**
    ```bash
    cd services/pdf-generation-service
    ```
2.  **Run tests:**
    ```bash
    python -m unittest tests/test_app.py
    ```