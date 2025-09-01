# PDF Generation Service TODO List

This file tracks specific tasks for the PDF Generation Service.

## Core Logic Implementation

*   **Data Retrieval:**
    *   Implement logic to retrieve all necessary calculation results and metadata for a given `project_id` from the PostgreSQL database.
    *   Ensure efficient and secure database queries.
*   **Templating:**
    *   Choose and integrate a Python templating engine (e.g., Jinja2).
    *   Design and create HTML/CSS templates for the solar report, incorporating all relevant data points (energy yield, shading analysis, financial data, etc.).
    *   Ensure templates are dynamic and can handle varying data structures.
*   **PDF Rendering:**
    *   Integrate a PDF rendering library (e.g., WeasyPrint) to convert the generated HTML/CSS into a high-quality PDF document.
    *   Configure PDF output settings (e.g., page size, margins, fonts).

## API Endpoint

*   Implement the `GET /api/download/:project_id` endpoint:
    *   Receive `project_id` from the API Gateway (which has already vetted payment status).
    *   Trigger data retrieval, templating, and PDF rendering.
    *   Return the generated PDF as a file download.

## Performance & Scalability

*   Optimize PDF generation for speed, especially for complex reports.
*   Consider caching generated PDFs for frequently accessed reports.

## Testing

*   Develop unit tests for data retrieval, templating, and PDF rendering components.
*   Create integration tests for the `/api/download/:project_id` endpoint.

## Future Enhancements

*   Add support for different report layouts or customization options.
*   Implement asynchronous PDF generation for very large reports.
*   Integrate with a document storage solution (e.g., S3) for long-term storage of generated PDFs.
