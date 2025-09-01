# Sol-Calc.com

This is a self-hostable solar planning and calculation product based on the technical architecture defined in `GEINI.md`.

## Running the Application

To run the application, you need to have Docker and Docker Compose installed.

1. **Clone the repository** (or have the files in your local directory).

2. **Run the application using Docker Compose:**

   ```bash
   docker compose up -d --build
   ```
   *Ensure your `.env` file at the project root is correctly configured with necessary environment variables (e.g., database credentials, Stripe API keys).*

3. **Access the application:**

   *   Frontend: [http://localhost:3000](http://localhost:3000)
   *   API Gateway: [http://localhost:9080](http://localhost:9080)

## Services

*   **Frontend:** A React application that provides the user interface.
*   **API Gateway:** Apache APISIX that routes traffic to the backend services. (Core routing, rate limiting, and payment gating implemented, but startup issues persist).
*   **Calculation Service:** A Python service that performs the solar calculations.
*   **Payment Service:** A Python service that handles payments with Stripe. (Core implementation complete).
*   **PDF Generation Service:** A Python service that generates PDF reports. (Core implementation complete).
*   **Database:** A PostgreSQL database with PostGIS for storing project data. (Schema finalized for projects and calculations).
