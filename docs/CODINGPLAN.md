# Coding Plan for Sol-Calc.com

This document outlines the development plan for the Sol-Calc project, organized into phases.

## Phase 1: Core Backend Services

This phase focuses on implementing the foundational backend microservices.

### `payment-service` (Completed)

*   **Status:** Core implementation complete. Integrates with Stripe for checkout sessions and handles webhooks to update payment status in the database. Enhanced for security and compliance.
*   **Next Steps:** Ongoing maintenance, minor enhancements, and integration with the frontend.

### `calculation-service`

*   **Objective:** To perform complex solar modeling based on LIDAR data and other inputs.
*   **Key Tasks:**
    *   Develop robust LIDAR data parsing and processing (e.g., using `laspy` or `PDAL`).
    *   Implement 3D terrain model generation and storage in PostGIS.
    *   Integrate `PVLib Python` for high-fidelity solar simulation.
    *   Calculate annual energy yield, shading losses, and optimal panel placement.
    *   Persist calculation results and project metadata in the PostgreSQL database.

### `pdf-generation-service`

*   **Objective:** To generate comprehensive PDF reports based on calculation results.
*   **Key Tasks:**
    *   Retrieve all necessary calculation results and project metadata from the PostgreSQL database.
    *   Utilize a templating engine (e.g., Jinja2) to create dynamic HTML/CSS report layouts.
    *   Render the HTML to a PDF using a library like WeasyPrint.
    *   Provide the generated PDF as a file download.

### API Gateway (Apache APISIX)

*   **Objective:** To serve as the single entry point for all API traffic, handling routing, security, and payment gating.
*   **Key Tasks:**
    *   Configure dynamic routing rules to direct traffic to the appropriate microservices (`/api/calculate`, `/api/checkout`, `/api/download/:project_id`).
    *   Implement rate limiting to protect backend services.
    *   Develop a custom Lua plugin or serverless function to enforce payment gating for PDF downloads, performing a fast database lookup for project status.

### Database (PostgreSQL/PostGIS)

*   **Objective:** To store all project, calculation, and payment-related data, including geospatial LIDAR data.
*   **Key Tasks:**
    *   Finalize the database schema for `projects`, `calculations`, and other related tables.
    *   Ensure proper indexing and optimization for performance.
    *   Implement secure database connection management.

## Phase 2: Frontend Application

This phase focuses on building the interactive user interface.

*   **Technology:** React, Vue.js, or a similar modern framework.
*   **Key Features:**
    *   **Data Wizard:** A multi-step form for collecting project details (location, panel type, ground mount specifications, LIDAR file uploads).
    *   **3D Visualizer:** Integration of a WebGL library (e.g., three.js) to render terrain from LIDAR data and allow interactive panel placement/orientation.
    *   **Asynchronous Processing:** Display loading states and poll status endpoints for long-running calculations.
    *   **Payment Integration:** Seamless integration with the `payment-service` for checkout and payment redirects.
    *   **Report Download:** Functionality to trigger and download the generated PDF reports.

## Phase 3: Advanced Features & Infrastructure

This phase includes additional features and robust infrastructure setup.

*   **User Management:** Implement user authentication, authorization, and profile management.
*   **Project History:** Allow users to view and manage their past projects and calculations.
*   **CI/CD Pipeline:** Set up automated testing, building, and deployment pipelines.
*   **Monitoring & Logging:** Implement comprehensive monitoring, logging, and alerting for all services.
*   **Security Audits:** Conduct regular security audits and penetration testing.
*   **Performance Optimization:** Optimize services for scalability and performance.
*   **Secrets Management:** Implement a robust secrets management solution (e.g., HashiCorp Vault) for production credentials.