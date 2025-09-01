# Frontend TODO List

This file tracks specific tasks for the Frontend Single Page Application (SPA).

## Core UI Development

*   **Data Wizard:**
    *   Design and implement a multi-step form for collecting project details (location, panel type, ground mount specifications).
    *   Implement LIDAR file upload functionality.
    *   Ensure form validation and user-friendly navigation between steps.
*   **3D Visualizer:**
    *   Integrate a WebGL library (e.g., three.js) to render the terrain from LIDAR data.
    *   Allow users to interactively position and orient solar panels on the 3D terrain.
    *   Display real-time feedback on panel placement (e.g., shading analysis visualization).
*   **Asynchronous Processing Feedback:**
    *   Display loading states and progress indicators while the Calculation Service is processing requests.
    *   Implement polling mechanism to check the status endpoint of the Calculation Service to determine when the report is ready.

## API Integration

*   Integrate with the backend APIs:
    *   Call `POST /api/calculate` to initiate solar calculations.
    *   Call `POST /api/checkout` to initiate the payment flow with the Payment Service.
    *   Handle the payment redirect from Stripe.
    *   Call `GET /api/download/:project_id` to download the generated PDF report.

## User Experience (UX) & Design

*   Apply a consistent and modern UI/UX design (e.g., using Bootstrap CSS and Material Design principles).
*   Ensure responsiveness across various devices (desktop, tablet, mobile).
*   Implement clear error messages and user feedback.

## Testing

*   Develop unit tests for UI components.
*   Implement integration tests for API calls and data flow.
*   Conduct end-to-end tests for the entire user journey.

## Future Enhancements

*   Implement user authentication and account management.
*   Add project history and management features.
*   Improve 3D visualizer with more advanced rendering and interaction.
