# Payment Service

This service is responsible for handling payments with Stripe.

## API

*   **POST /api/checkout:** Creates a new Stripe checkout session.
*   **POST /webhooks/stripe:** Receives webhooks from Stripe to update the payment status.
