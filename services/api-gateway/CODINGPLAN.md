# API Gateway Coding Plan

This file outlines the development plan for the Apache APISIX API Gateway.

## Phase 1: Basic Routing and Rate Limiting (Completed)

*   **Objective:** Establish core routing functionality and basic protection for backend services.
*   **Status:** Completed. Routes for `calculation-service`, `payment-service`, and `pdf-generation-service` are defined, and rate limiting is implemented.

## Phase 2: Payment Gating Implementation (Completed)

*   **Objective:** Secure the PDF download endpoint by enforcing payment verification.
*   **Status:** Completed. A custom Lua plugin is developed and integrated with the `/api/download/:project_id` route to check payment status from the database and return HTTP 402 if not paid.

## Phase 3: Advanced Features and Hardening

*   **Objective:** Enhance security, observability, and traffic management capabilities.
*   **Tasks:**
    *   Configure detailed access logs and integrate with a centralized logging system.
    *   Set up monitoring dashboards and alerts for key APISIX metrics.
    *   Explore and implement additional security features like WAF integration or authentication plugins.
    *   Investigate and apply advanced traffic management policies (e.g., load balancing algorithms, circuit breakers).
