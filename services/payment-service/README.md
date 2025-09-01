# Payment Service

This service is responsible for handling payments with Stripe and updating project statuses in the database.

## API Endpoints

*   **POST /api/checkout:** Initiates a Stripe checkout session for a given `project_id`.
    *   **Request Body:** `{"project_id": "unique_id"}`
    *   **Response:** `{"checkout_url": "https://checkout.stripe.com/..."}`

*   **POST /webhooks/stripe:** Receives and processes webhook events from Stripe, primarily to update the payment status of projects.
    *   This endpoint verifies the webhook signature for security.

*   **GET /health:** A basic health check endpoint that also verifies database connectivity.
    *   **Response:** `"OK"` (200) on success, or an error message (500) on failure.

## Environment Variables

This service requires the following environment variables to be set:

*   `STRIPE_SECRET_KEY`: Your Stripe secret API key. Obtain this from your [Stripe Dashboard](https://dashboard.stripe.com/apikeys).
*   `STRIPE_WEBHOOK_SECRET`: The secret used to verify Stripe webhook signatures. Generate this when setting up a webhook endpoint in your [Stripe Dashboard](https://dashboard.stripe.com/webhooks).
*   `STRIPE_PRODUCT_PRICE_ID`: The ID of the Stripe Price object for the product being sold. This typically starts with `price_...`. This variable is mandatory.
*   `STRIPE_SUCCESS_URL`: The URL to redirect users to after a successful checkout session.
*   `STRIPE_CANCEL_URL`: The URL to redirect users to if they cancel the checkout session.
*   `DATABASE_URL`: The connection string for your PostgreSQL database. Example: `postgresql://user:password@host:port/database_name`.

It is recommended to use a `.env` file for local development.

## Running the Service

### Prerequisites

*   Python 3.9+
*   `pip`
*   Docker (optional, for containerized deployment)

### Local Development

1.  **Navigate to the service directory:**
    ```bash
    cd services/payment-service
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file:**
    ```
    STRIPE_SECRET_KEY=sk_test_...
    STRIPE_WEBHOOK_SECRET=whsec_...
    STRIPE_PRODUCT_PRICE_ID=price_...
    STRIPE_SUCCESS_URL=https://yourdomain.com/success
    STRIPE_CANCEL_URL=https://yourdomain.com/cancel
    DATABASE_URL=postgresql://user:password@localhost:5432/solcalc_db
    ```
    *Replace with your actual values.*

4.  **Run the application:**
    ```bash
    python app.py
    ```
    The service will run on `http://0.0.0.0:5003`.

### Docker

1.  **Navigate to the service directory:**
    ```bash
    cd services/payment-service
    ```
2.  **Build the Docker image:**
    ```bash
    docker build -t payment-service .
    ```
3.  **Run the Docker container:**
    ```bash
    docker run -p 5003:5003 --env-file .env payment-service
    ```
    *Ensure your `.env` file is correctly configured as described above.*

## Testing

To run the unit tests for this service:

1.  **Navigate to the service directory:**
    ```bash
    cd services/payment-service
    ```
2.  **Run tests:**
    ```bash
    python -m unittest tests/test_app.py
    ```

## Compliance and Security Considerations

Given the sensitive nature of this application (DoD contractor, government use), adherence to compliance standards like GDPR, SOC 2, and PCI DSS is paramount. While this service offloads cardholder data handling to Stripe (significantly reducing direct PCI scope), the following considerations are crucial:

*   **Secrets Management:** For production deployments, relying solely on environment variables is insufficient. Implement a robust secrets management solution (e.g., Kubernetes Secrets, AWS Secrets Manager, HashiCorp Vault) to securely store and inject `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and `DATABASE_URL`.
*   **Logging:** Ensure that no Personally Identifiable Information (PII) or sensitive data is logged. Implement strict logging policies and review logs regularly for compliance.
*   **Container Security:** The Dockerfile now includes running the application as a non-root user (`appuser`), which is a security best practice to limit potential damage in case of a container compromise.
*   **Database Connection Pooling:** For high-traffic production environments, consider implementing a database connection pool (e.g., using `SQLAlchemy` with a connection pool or an external tool like `pgbouncer`) to efficiently manage database connections and prevent resource exhaustion.
*   **Dependency Scanning:** Regularly scan all project dependencies for known vulnerabilities using tools like Snyk, Dependabot, or OWASP Dependency-Check. Integrate this into your CI/CD pipeline.
*   **Input Validation:** While basic validation is in place, ensure all inputs are rigorously validated and sanitized to prevent injection attacks and other vulnerabilities.
*   **Error Handling:** Implement comprehensive error handling and alerting mechanisms to quickly detect and respond to security incidents or system failures.
*   **Audit Trails:** Ensure that all significant actions and data access are logged for audit purposes, supporting SOC 2 compliance.
*   **Data Minimization:** This service only processes `project_id` and payment status. Ensure that no unnecessary personal data is collected or stored, aligning with GDPR principles.
