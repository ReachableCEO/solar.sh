# API Gateway Coding Plan

This file outlines the development plan for the Apache APISIX API Gateway.

## Phase 1: Basic Routing and Rate Limiting

*   **Objective:** Establish core routing functionality and basic protection for backend services.
*   **Tasks:**
    *   Define routes in `config.yaml` to direct traffic to the `calculation-service`, `payment-service`, and `pdf-generation-service`.
    *   Implement global or per-route rate limiting policies.

## Phase 2: Payment Gating Implementation

*   **Objective:** Secure the PDF download endpoint by enforcing payment verification.
*   **Tasks:**
    *   Develop a custom Lua plugin for APISIX that queries the PostgreSQL database (via a fast lookup) to check the payment status of a `project_id`.
    *   Integrate this plugin with the `/api/download/:project_id` route.
    *   Ensure the plugin returns an HTTP 402 status if the project is not paid.
    *   Alternatively, explore serverless function integration for payment gating if more complex logic is required.

## Phase 3: Advanced Features and Hardening

*   **Objective:** Enhance security, observability, and traffic management capabilities.
*   **Tasks:**
    *   Configure detailed access logs and integrate with a centralized logging system.
    *   Set up monitoring dashboards and alerts for key APISIX metrics.
    *   Explore and implement additional security features like WAF integration or authentication plugins.
    *   Investigate and apply advanced traffic management policies (e.g., load balancing algorithms, circuit breakers).
