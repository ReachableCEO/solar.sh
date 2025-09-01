# Frontend Coding Plan

This file outlines the development plan for the Frontend Single Page Application (SPA).

## Phase 1: Core Data Wizard and Basic Layout

*   **Objective:** Create the foundational multi-step form for data input.
*   **Tasks:**
    *   Set up the chosen frontend framework (React/Vue) and project structure.
    *   Design and implement the basic layout for the data wizard, including navigation between steps.
    *   Develop input fields for project details (location, panel type, etc.).
    *   Implement basic form validation.
    *   Create a component for LIDAR file uploads.

## Phase 2: 3D Visualizer Integration and API Calls

*   **Objective:** Integrate the 3D visualization and connect to the backend calculation service.
*   **Tasks:**
    *   Integrate a WebGL library (e.g., three.js) into the application.
    *   Develop logic to render the 3D terrain model from uploaded LIDAR data.
    *   Implement interactive controls for positioning and orienting solar panels on the 3D model.
    *   Integrate API calls to the `calculation-service` (`POST /api/calculate`).
    *   Display loading states and poll for calculation status updates.

## Phase 3: Payment and PDF Download Integration

*   **Objective:** Enable users to pay for and download their reports.
*   **Tasks:**
    *   Integrate with the `payment-service` by calling `POST /api/checkout`.
    *   Handle the redirect to and from Stripe's checkout page.
    *   Implement the functionality to call `GET /api/download/:project_id` and handle the PDF file download (backend PDF service is ready for integration).

## Phase 4: UI/UX Refinements and Advanced Features

*   **Objective:** Polish the user experience and add advanced functionalities.
*   **Tasks:**
    *   Apply consistent styling and ensure responsiveness across devices.
    *   Implement user authentication and account management (if applicable).
    *   Develop features for project history and management.
    *   Continuously improve the 3D visualizer's performance and features.
