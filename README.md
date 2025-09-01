# Sol-Calc.com

This is a self-hostable solar planning and calculation product based on the technical architecture defined in `GEINI.md`.

## Running the Application

To run the application, you need to have Docker and Docker Compose installed.

1. **Clone the repository** (or have the files in your local directory).

2. **Run the application using Docker Compose:**

   ```bash
   docker-compose up -d
   ```

3. **Access the application:**

   *   Frontend: [http://localhost:3000](http://localhost:3000)
   *   API Gateway: [http://localhost:9080](http://localhost:9080)

## Services

*   **Frontend:** A React application that provides the user interface.
*   **API Gateway:** Apache APISIX that routes traffic to the backend services.
*   **Calculation Service:** A Python service that performs the solar calculations.
*   **Payment Service:** A Python service that handles payments with Stripe.
*   **PDF Generation Service:** A Python service that generates PDF reports.
*   **Database:** A PostgreSQL database with PostGIS for storing project data.
