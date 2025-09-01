import os
import json
import psycopg2
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import io

app = Flask(__name__)

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

@app.route('/api/download/<project_id>', methods=['GET'])
def download_pdf(project_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Retrieve project data
        cur.execute(
            "SELECT project_name, location_lat, location_lon, cost_usd, status, metadata FROM projects WHERE id = %s",
            (project_id,)
        )
        project_data = cur.fetchone()
        if not project_data:
            return jsonify({"error": "Project not found"}), 404
        
        project_name, location_lat, location_lon, cost_usd, status, metadata = project_data

        # Retrieve calculation data
        cur.execute(
            "SELECT annual_kwh, shading_loss_pct, financial_data FROM calculations WHERE project_id = %s",
            (project_id,)
        )
        calculation_data = cur.fetchone()
        
        cur.close()
        conn.close()

        if not calculation_data:
            return jsonify({"error": "Calculation results not found for this project"}), 404

        annual_kwh, shading_loss_pct, financial_data = calculation_data

        # Prepare data for template
        report_data = {
            "project_id": project_id,
            "project_name": project_name,
            "location": {"lat": location_lat, "lon": location_lon},
            "cost_usd": cost_usd,
            "status": status,
            "annual_kwh": annual_kwh,
            "shading_loss_pct": shading_loss_pct,
            "financial_data": financial_data,
            "metadata": metadata,
            "generation_date": os.getenv('GENERATION_DATE', 'N/A') # Example of dynamic data
        }

        # Load and render HTML template
        template = env.get_template('report_template.html')
        html_out = template.render(report=report_data)

        # Generate PDF
        pdf_file = HTML(string=html_out).write_pdf()

        # Return PDF as a file download
        return send_file(
            io.BytesIO(pdf_file),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'solar_report_{project_id}.pdf'
        )

    except psycopg2.Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": f"Database operation failed: {e}"}), 500
    except Exception as e:
        app.logger.error(f"PDF generation error: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return "OK", 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return "Database connection failed", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)