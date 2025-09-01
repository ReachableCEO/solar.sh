# API Gateway TODO List

This file tracks specific tasks for the Apache APISIX API Gateway.

## Core Configuration (Completed)

*   Configure dynamic routing for all microservices:
    *   `/api/calculate` -> Calculation Service
    *   `/api/checkout` -> Stripe Payment Service
    *   `/api/download/:project_id` -> PDF Generation Service
    *   `/webhooks/stripe` -> Stripe Payment Service
*   Implement rate limiting to protect backend services from abuse.

## Payment Gating (Completed)

*   Develop a custom Lua plugin or serverless function within APISIX to enforce payment gating for PDF downloads (`/api/download/:project_id`).
    *   This plugin/function must perform a fast database lookup to verify that the `project_id` has a "paid" status.
    *   If not paid, return an HTTP 402 Payment Required error immediately.

## Security & Observability

*   Implement robust logging for API requests and responses.
*   Configure monitoring and alerting for API Gateway performance and errors.
*   Ensure secure communication (HTTPS) is enforced at the gateway level.

## Future Enhancements

*   Implement API key management for external integrations.
*   Explore advanced traffic management features (e.g., load balancing, circuit breaking).
