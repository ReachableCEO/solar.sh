# Gemini's Operating Principles and Development Plan

This document outlines my operating principles and my plan for working on the Sol-Calc.com project. It is intended to be a living document that I will update as I make progress.

## 1. Operating Principles

*   **Adherence to Instructions:** I will follow all instructions given to me precisely. I will not deviate from the instructions without explicit permission. If an instruction is unclear, I will ask for clarification.
*   **Architectural Integrity:** I will adhere strictly to the architectural decisions documented in the `docs/` directory. I will not make unilateral architectural changes. My work on the API Gateway will be focused on implementing it using **Apache APISIX** as planned.
*   **Code Quality:** I will write clean, efficient, and well-documented code. I will ensure that all code is accompanied by comprehensive unit tests.
*   **Documentation:** I will maintain accurate and consistent documentation. I will use the `STATUS-GEMINI.md` file to track my progress, and I will keep the shared documentation in the `docs/` directory up-to-date.

## 2. Architectural Understanding

I understand that the Sol-Calc.com project is a microservices-based application with the following components:

*   **Frontend:** A React-based single-page application.
*   **API Gateway (Apache APISIX):** The single entry point for all API traffic, responsible for routing, rate limiting, and payment gating.
*   **Calculation Service:** A Python service for performing solar calculations.
*   **Payment Service:** A Python service for handling Stripe payments.
*   **PDF Generation Service:** A Python service for generating PDF reports.
*   **Database:** A PostgreSQL database with PostGIS for data storage.

I will ensure that my work respects the boundaries and responsibilities of each of these services.

## 3. Development Plan

My high-level development plan is as follows:

1.  **API Gateway (APISIX):** I will start by implementing the API Gateway using Apache APISIX, as this is a critical piece of infrastructure that is currently incorrect. I will implement routing to all services and the payment gating logic.
2.  **PDF Generation Service:** I will remove the payment gating logic from this service and ensure that it is fully compliant with the architecture.
3.  **Database:** I will apply the Alembic migrations to ensure the database schema is up-to-date.
4.  **Core Calculation Logic:** I will complete the implementation of the calculation service, including the full LIDAR data processing and solar modeling.
5.  **Payment Service:** I will complete the Stripe integration and ensure that it is fully tested.
6.  **Frontend:** I will build out the frontend, including the data wizard and 3D visualizer.

## 4. Collaboration

I am committed to working in parallel with "Claude code" in a productive and collaborative manner. I will ensure that all shared documentation is kept up-to-date and that my work is clearly communicated through commit messages and status updates. I will do my best to assist "Claude code" and ensure that we both have the best chance to succeed.
