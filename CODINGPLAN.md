# Coding Plan

This file outlines the development plan for the Sol-Calc project.

## Phase 1: Core Functionality

### `calculation-service`

- [ ] Define the inputs for the solar calculation (e.g., address, roof size, etc.).
- [ ] Implement the solar calculation logic.
- [ ] Store the results of the calculation in the database.

### `payment-service`

- [ ] Integrate with the Stripe API to create checkout sessions.
- [ ] Handle Stripe webhooks to update the payment status in the database.

### `pdf-generation-service`

- [ ] Create a PDF template for the solar report.
- [ ] Populate the PDF template with the results of the solar calculation.

### Database

- [ ] Define the database schema for the projects, calculations, and payments.
- [ ] Implement the database integration for each service.

## Phase 2: Frontend

- [ ] Create a form to input the data for the solar calculation.
- [ ] Display the results of the solar calculation.
- [ ] Integrate with the `payment-service` to allow users to pay for the report.
- [ ] Allow users to download the PDF report.

## Phase 3: Advanced Features

- [ ] User authentication and accounts.
- [ ] Project history and management.
- [ ] 3D visualization of the solar installation.
