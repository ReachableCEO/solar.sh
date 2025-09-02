# Coding Plan for Sol-Calc.com

This document outlines the development plan for the Sol-Calc project, organized into phases.

## Phase 1: Core Backend Services

This phase focuses on implementing the foundational backend microservices.

### `payment-service`

*   **Status:** In Progress. Integrates with Stripe for checkout sessions and handles webhooks to update payment status in the database. 
*   **Next Steps:** Needs to be fully integrated with the frontend.

### `calculation-service`

*   **Objective:** To perform complex solar modeling based on LIDAR data and other inputs.
*   **Key Tasks:**
    *   Develop robust LIDAR data parsing and processing (e.g., using `laspy` or `PDAL`).
    *   Implement 3D terrain model generation and storage in PostGIS.
    *   Integrate `PVLib Python` for high-fidelity solar simulation.
    *   Calculate annual energy yield, shading losses, and optimal panel placement.
    *   Persist calculation results and project metadata in the PostgreSQL database.

### `pdf-generation-service`

*   **Status:** In Progress. Generates comprehensive PDF reports based on calculation results, utilizing Jinja2 for templating and WeasyPrint for rendering. Provides the generated PDF as a file download.
*   **Next Steps:** Payment gating logic needs to be removed from this service and moved to the API Gateway.

### API Gateway (Apache APISIX)

*   **Objective:** To serve as the single entry point for all API traffic, handling routing, security, and payment gating.
*   **Status:** Not started. The previous implementation was done in Nginx and needs to be reverted to APISIX.
*   **Key Tasks:**
    *   Implement dynamic routing.
    *   Implement rate limiting.
    *   Implement the custom Lua plugin for payment gating.

### Database (PostgreSQL/PostGIS)

*   **Status:** In Progress. The database schema for `projects` and `calculations` is finalized. 
*   **Next Steps:** The initial Alembic migration needs to be applied.

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