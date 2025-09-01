# Frontend

This is a React application that provides the user interface for Sol-Calc.com.

## Overview

The frontend is a Single Page Application (SPA) designed to be highly interactive. It communicates with the backend microservices via the API Gateway to:

*   Collect project details through a multi-step data wizard.
*   Allow LIDAR file uploads.
*   Render 3D visualizations of terrain and panel placements.
*   Initiate solar calculations.
*   Handle payment flows.
*   Download generated PDF reports.

## Technologies

*   React
*   (Potentially) three.js for 3D visualization
*   (Potentially) Bootstrap or other CSS framework for styling

## Running the Application

### Prerequisites

*   Node.js (LTS version recommended)
*   npm or yarn
*   Docker (optional, for containerized deployment)

### Local Development

1.  **Navigate to the frontend directory:**
    ```bash
    cd services/frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Start the development server:**
    ```bash
    npm start
    ```
    The application will typically run on `http://localhost:3000`.

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

Alternatively, to run only this service with Docker (for isolated testing/development):

1.  **Navigate to the service directory:**
    ```bash
    cd services/frontend
    ```
2.  **Build the Docker image:**
    ```bash
    docker build -t frontend .
    ```
3.  **Run the Docker container:**
    ```bash
    docker run -p 3000:3000 frontend
    ```

## Integration with Backend

The frontend communicates with the backend services through the API Gateway, which is typically exposed on port `9080` (e.g., `http://localhost:9080`). API calls from the frontend should be directed to this gateway.

## Testing

To run the unit tests for this application:

1.  **Navigate to the frontend directory:**
    ```bash
    cd services/frontend
    ```
2.  **Run tests:**
    ```bash
    npm test
    ```