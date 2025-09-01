 Technical Architecture for Sol-Calc.com
This document provides a detailed technical blueprint for building a fully AGPLv3-licensed and self-hostable solar planning and calculation product. It is intended for software engineers and includes information on the architecture, data flow, API endpoints, and database schema.
1. Architectural Overview üèóÌøóÔ∏è
The application is built on a containerized, microservices architecture using Docker and Docker Compose. An API gateway orchestrates all external traffic, ensuring a secure and efficient flow of data.


graph TD
    A[User/Client] -->|Input Data (via Web UI)| B(Frontend)
    B -->|API Calls (e.g., /api/calculate)| C(APISIX API Gateway)
    C -->|Routes & Rate Limits| D(Calculation Service)
    C -->|Routes & Gating| E(PDF Generation Service)
    C -->|Routes & Webhooks| F(Stripe Payment Service)
    D -->|Persists Project & Results| G(PostgreSQL/PostGIS DB)
    E -->|Retrieves Project & Results| G
    F -->|Updates Project Status| G
    H[Stripe] -->|Webhook: checkout.session.completed| F

3. Core Components and Technologies üõ†Ìª†Ô∏è
a. Web Frontend
The user interface is a wizard-style Single Page Application (SPA) designed to be highly interactive. It sends data to the backend APIs and handles the payment redirect and PDF download.
 * Technology: React, Vue.js, or a similar modern framework.
 * Key Features:
   * Data Wizard: A multi-step form for collecting project details (e.g., location, panel type, ground mount specifications) and accepting LIDAR file uploads.
   * 3D Visualizer: Uses a WebGL library like three.js to render the terrain from LIDAR data and allow users to position and orient panels.
   * Async Processing: Displays a loading state while the Calculation Service is processing the request, and polls a status endpoint to determine when the report is ready.
b. API Gateway (Apache APISIX)
Apache APISIX serves as the single point of entry for all API traffic. It is crucial for security, routing, and implementing the payment-gating logic.
 * Project: Apache APISIX
 * Role:
   * Dynamic Routing: Configured to direct traffic based on the URI.
     * /api/calculate -> Calculation Service
     * /api/checkout -> Stripe Payment Service
     * /api/download/:project_id -> PDF Generation Service (with gating logic)
   * Security: Enforces rate limiting to protect the backend services from abuse.
   * Payment Gating: APISIX is the final gatekeeper for the PDF download. It will use a custom Lua plugin or a serverless function to perform a fast database lookup. This check verifies that the project_id has a "paid" status before routing the request to the PDF service. If not, it immediately returns an HTTP 402 Payment Required error.
c. Calculation Service
This service performs the heavy lifting. It ingests large LIDAR and weather datasets and runs complex solar modeling algorithms.
 * Technology: Python is recommended for its mature scientific libraries.
 * API Endpoint: POST /api/calculate
 * Request Body (Example):
   {
  "project_name": "Ground Mount Project 1",
  "location": { "lat": 35.79, "lon": -78.78 },
  "lidar_data": "<base64_encoded_lidar_file>",
  "panel_specs": { ... },
  "ground_mount_config": { ... }
}

 * Core Logic:
   * LIDAR Processing: The service uses laspy or PDAL to parse the .las or .laz file. The output is a highly detailed mesh or point cloud that's stored in the PostGIS database.
   * Solar Modeling: Utilizes PVLib Python to perform a high-fidelity solar simulation using the 3D terrain model and weather data. It calculates annual energy yield, shading losses, and optimal panel placement.
 * Output: Returns a project_id and a status code indicating that the calculation has started.
d. Stripe Payment Service
This service is solely responsible for handling the one-time payment flow and confirming payment status via webhooks. It is completely decoupled from the calculation logic.
 * Technology: A lightweight web framework like Python's Flask or FastAPI.
 * API Endpoint: POST /api/checkout
   * Request Body: { "project_id": "unique_id" }
   * Response: { "checkout_url": "https://checkout.stripe.com/..." }
 * Webhook Endpoint: POST /webhooks/stripe
   * Logic: Listens for the checkout.session.completed event from Stripe. The event payload will contain the project_id in its metadata.
   * Database Update: Upon a valid event, it updates the projects table for the corresponding project_id, changing the status from 'pending' to 'paid'. This is a fast, critical operation. Best practices dictate returning a 200 OK response to Stripe immediately and handling any further logic asynchronously.
e. PDF Generation Service
This service is a stateless endpoint that creates the final report.
 * Technology: A Python service using a library like WeasyPrint.
 * API Endpoint: GET /api/download/:project_id
 * Logic:
   * Receives a project_id from APISIX (which has already vetted the payment status).
   * Retrieves all calculation results and metadata for that project from the PostgreSQL database.
   * Uses a templating engine (e.g., Jinja2) to create an HTML/CSS file.
   * Renders the HTML to a PDF using WeasyPrint.
   * Returns the generated PDF as a file download.
3. Database Schema üóÑÌ∑ÑÔ∏è
The database is built on PostgreSQL with PostGIS to handle both structured and geospatial data.
 * Project: PostgreSQL and PostGIS
 * Core Tables:
   * projects:
     * id (UUID, PK)
     * created_at (TIMESTAMP)
     * status (VARCHAR, e.g., 'pending', 'paid', 'error')
     * cost_usd (NUMERIC)
     * lidar_geom (GEOMETRY, using PostGIS to store the point cloud or mesh)
     * ...and other project metadata.
   * calculations:
     * id (UUID, PK)
     * project_id (UUID, FK to projects)
     * annual_kwh (NUMERIC)
     * shading_loss_pct (NUMERIC)
     * financial_data (JSONB)
     * ...and other calculation result
