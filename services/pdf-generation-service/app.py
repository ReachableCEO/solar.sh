import os
import json
import psycopg2
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file, g
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import io
import logging
import hashlib
import time
from functools import wraps

app = Flask(__name__, template_folder='templates')

# Security configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-in-production')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Configure logging with compliance requirements
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # In production, add file handler for audit logs
    ]
)
logger = logging.getLogger(__name__)

# Configure caching with security considerations
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # Use Redis in production for better security
    'CACHE_DEFAULT_TIMEOUT': 3600,  # Cache for 1 hour
    'CACHE_KEY_PREFIX': 'pdf_gen_',
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"],
    storage_uri="memory://",  # Use Redis in production
)

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# Font configuration for WeasyPrint
font_config = FontConfiguration()

# Security middleware
@app.after_request
def add_security_headers(response):
    """Add security headers for compliance"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

def audit_log(action, resource, user_id=None, details=None):
    """Log actions for compliance auditing"""
    log_entry = {
        'timestamp': time.time(),
        'action': action,
        'resource': resource,
        'user_id': user_id or 'anonymous',
        'ip_address': get_remote_address(),
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'details': details or {}
    }
    logger.info(f"AUDIT: {log_entry}")

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise

# Setup Jinja2 environment
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

@app.route('/api/download/<project_id>', methods=['GET', 'HEAD'])
@limiter.limit("20 per hour; 5 per minute")
def download_pdf(project_id):
    # Audit log the access attempt
    audit_log('pdf_download_attempt', f'project:{project_id}')

    # Handle HEAD requests for availability checking
    if request.method == 'HEAD':
        return check_pdf_available(project_id)

    # Create cache key that includes query parameters for customization
    format_type = request.args.get('format', 'detailed')
    include_financial = request.args.get('include_financial', 'true').lower() == 'true'
    cache_key = f'pdf_{project_id}_{format_type}_{include_financial}'

    # Check cache first
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response
    try:
        # Validate project_id format
        try:
            uuid.UUID(project_id)
        except ValueError:
            return jsonify({"error": "Invalid project ID format"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Retrieve project data
        cur.execute(
            "SELECT project_name, location_lat, location_lon, cost_usd, status, metadata, created_at FROM projects WHERE id = %s",
            (project_id,)
        )
        project_data = cur.fetchone()
        if not project_data:
            cur.close()
            conn.close()
            return jsonify({"error": "Project not found"}), 404

        project_name, location_lat, location_lon, cost_usd, status, metadata, created_at = project_data

        # Check if project is paid (only allow downloads for paid projects)
        if status != 'paid':
            cur.close()
            conn.close()
            return jsonify({"error": "Project must be paid before PDF download is available"}), 403

        # Retrieve calculation data
        cur.execute(
            "SELECT annual_kwh, shading_loss_pct, financial_data, created_at FROM calculations WHERE project_id = %s ORDER BY created_at DESC LIMIT 1",
            (project_id,)
        )
        calculation_data = cur.fetchone()

        cur.close()
        conn.close()

        if not calculation_data:
            return jsonify({"error": "Calculation results not found for this project"}), 404

        annual_kwh, shading_loss_pct, financial_data, calc_created_at = calculation_data

        # Parse financial data if it's stored as JSON
        try:
            if isinstance(financial_data, str):
                financial_data = json.loads(financial_data)
        except (json.JSONDecodeError, TypeError):
            financial_data = {}

        # Parse metadata if it's stored as JSON
        try:
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
        except (json.JSONDecodeError, TypeError):
            metadata = {}

        # Calculate additional metrics
        net_annual_kwh = annual_kwh * (1 - shading_loss_pct) if annual_kwh and shading_loss_pct else annual_kwh
        cost_per_kwh = cost_usd / net_annual_kwh if net_annual_kwh and net_annual_kwh > 0 else 0

        # Prepare data for template
        report_data = {
            "project_id": project_id,
            "project_name": project_name or "Unnamed Project",
            "location": {
                "lat": location_lat,
                "lon": location_lon
            },
            "cost_usd": cost_usd or 0,
            "status": status,
            "annual_kwh": annual_kwh or 0,
            "net_annual_kwh": net_annual_kwh or 0,
            "shading_loss_pct": shading_loss_pct or 0,
            "cost_per_kwh": cost_per_kwh,
            "financial_data": financial_data if include_financial else {},
            "metadata": metadata,
            "project_created_at": created_at.isoformat() if created_at else None,
            "calculation_created_at": calc_created_at.isoformat() if calc_created_at else None,
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "format": format_type,
            "include_financial": include_financial
        }

        # Choose template based on format
        if format_type == 'summary':
            template_name = 'report_template_summary.html'
        elif format_type == 'detailed':
            template_name = 'report_template.html'
        else:
            template_name = 'report_template.html'

        # Load and render HTML template
        try:
            template = env.get_template(template_name)
        except:
            # Fallback to main template if specific template doesn't exist
            template = env.get_template('report_template.html')

        html_out = template.render(report=report_data)

        # Generate PDF with custom CSS
        css = CSS(string="""
            @page {
                size: A4;
                margin: 1in;
            }
            body {
                font-family: 'Helvetica', 'Arial', sans-serif;
                line-height: 1.6;
                color: #333;
            }
        """)

        pdf_file = HTML(string=html_out).write_pdf(stylesheets=[css], font_config=font_config)

        # Create the response
        response = send_file(
            io.BytesIO(pdf_file),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'solar_report_{project_name.replace(" ", "_")}_{project_id[:8]}_{format_type}.pdf'
        )

        # Audit log successful PDF generation
        audit_log('pdf_download_success', f'project:{project_id}', details={
            'format': format_type,
            'include_financial': include_financial,
            'file_size': len(pdf_file)
        })

        # Cache the response for 1 hour
        cache.set(cache_key, response, timeout=3600)

        return response

    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return jsonify({"error": "PDF generation failed"}), 500

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "healthy", "service": "pdf-generation-service"}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "service": "pdf-generation-service", "error": str(e)}, 500

def check_pdf_available(project_id):
    """Check if PDF is available for download without generating it"""
    try:
        # Validate project_id format
        try:
            uuid.UUID(project_id)
        except ValueError:
            return "", 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if project exists and is paid
        cur.execute(
            "SELECT status FROM projects WHERE id = %s",
            (project_id,)
        )
        project_data = cur.fetchone()

        if not project_data:
            cur.close()
            conn.close()
            return "", 404

        status = project_data[0]

        if status != 'paid':
            cur.close()
            conn.close()
            return "", 403

        # Check if calculation exists
        cur.execute(
            "SELECT 1 FROM calculations WHERE project_id = %s LIMIT 1",
            (project_id,)
        )
        calculation_exists = cur.fetchone() is not None

        cur.close()
        conn.close()

        if not calculation_exists:
            return "", 404

        return "", 200

    except Exception as e:
        logger.error(f"PDF availability check failed: {e}")
        return "", 500

@app.route('/api/cache/clear/<project_id>', methods=['POST'])
@limiter.limit("10 per hour")
def clear_pdf_cache(project_id):
    """Clear cached PDF for a specific project"""
    try:
        # Validate project_id format
        try:
            uuid.UUID(project_id)
        except ValueError:
            audit_log('cache_clear_failed', f'project:{project_id}', details={'error': 'invalid_uuid'})
            return jsonify({"error": "Invalid project ID format"}), 400

        # Clear the specific cache entry
        cache_key = f'pdf_{project_id}'
        cache.delete(cache_key)

        audit_log('cache_clear_success', f'project:{project_id}')
        logger.info(f"Cleared PDF cache for project {project_id}")
        return jsonify({"message": f"Cache cleared for project {project_id}"}), 200

    except Exception as e:
        audit_log('cache_clear_error', f'project:{project_id}', details={'error': str(e)})
        logger.error(f"Cache clear error: {e}")
        return jsonify({"error": "Failed to clear cache"}), 500

@app.route('/api/cache/clear-all', methods=['POST'])
@limiter.limit("5 per hour")
def clear_all_cache():
    """Clear all cached PDFs"""
    try:
        cache.clear()
        audit_log('cache_clear_all_success', 'all_projects')
        logger.info("Cleared all PDF caches")
        return jsonify({"message": "All PDF caches cleared"}), 200

    except Exception as e:
        audit_log('cache_clear_all_error', 'all_projects', details={'error': str(e)})
        logger.error(f"Cache clear all error: {e}")
        return jsonify({"error": "Failed to clear all caches"}), 500

@app.route('/api/data/privacy/<project_id>', methods=['DELETE'])
@limiter.limit("5 per hour")
def delete_project_data(project_id):
    """GDPR: Delete all data related to a project (right to erasure)"""
    try:
        # Validate project_id format
        try:
            uuid.UUID(project_id)
        except ValueError:
            audit_log('data_deletion_failed', f'project:{project_id}', details={'error': 'invalid_uuid'})
            return jsonify({"error": "Invalid project ID format"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if project exists
        cur.execute("SELECT id FROM projects WHERE id = %s", (project_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            audit_log('data_deletion_failed', f'project:{project_id}', details={'error': 'project_not_found'})
            return jsonify({"error": "Project not found"}), 404

        # Delete calculation data first (foreign key constraint)
        cur.execute("DELETE FROM calculations WHERE project_id = %s", (project_id,))

        # Delete project data
        cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))

        # Clear any cached PDFs for this project
        cache.delete(f'pdf_{project_id}')

        conn.commit()
        cur.close()
        conn.close()

        audit_log('data_deletion_success', f'project:{project_id}', details={'gdpr_compliant': True})
        logger.info(f"GDPR deletion completed for project {project_id}")

        return jsonify({
            "message": "Project data deleted successfully",
            "gdpr_compliant": True,
            "deleted_at": time.time()
        }), 200

    except Exception as e:
        audit_log('data_deletion_error', f'project:{project_id}', details={'error': str(e)})
        logger.error(f"Data deletion error: {e}")
        return jsonify({"error": "Failed to delete project data"}), 500

@app.route('/api/data/export/<project_id>', methods=['GET'])
@limiter.limit("10 per hour")
def export_project_data(project_id):
    """GDPR: Export all data related to a project (right to data portability)"""
    try:
        # Validate project_id format
        try:
            uuid.UUID(project_id)
        except ValueError:
            audit_log('data_export_failed', f'project:{project_id}', details={'error': 'invalid_uuid'})
            return jsonify({"error": "Invalid project ID format"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Retrieve project data
        cur.execute("""
            SELECT p.*, c.annual_kwh, c.shading_loss_pct, c.financial_data, c.created_at as calc_created_at
            FROM projects p
            LEFT JOIN calculations c ON p.id = c.project_id
            WHERE p.id = %s
        """, (project_id,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            audit_log('data_export_failed', f'project:{project_id}', details={'error': 'project_not_found'})
            return jsonify({"error": "Project not found"}), 404

        # Format data for export
        export_data = {
            "project_id": str(row[0]),
            "created_at": row[1].isoformat() if row[1] else None,
            "status": row[2],
            "cost_usd": float(row[3]) if row[3] else None,
            "project_name": row[4],
            "location_lat": float(row[5]) if row[5] else None,
            "location_lon": float(row[6]) if row[6] else None,
            "lidar_geom": str(row[7]) if row[7] else None,
            "metadata": row[8] if row[8] else {},
            "calculation_data": {
                "annual_kwh": float(row[9]) if row[9] else None,
                "shading_loss_pct": float(row[10]) if row[10] else None,
                "financial_data": row[11] if row[11] else {},
                "created_at": row[12].isoformat() if row[12] else None
            } if row[9] else None,
            "export_timestamp": time.time(),
            "gdpr_compliant": True
        }

        audit_log('data_export_success', f'project:{project_id}', details={'gdpr_compliant': True})
        logger.info(f"GDPR data export completed for project {project_id}")

        return jsonify(export_data), 200

    except Exception as e:
        import traceback
        audit_log('data_export_error', f'project:{project_id}', details={'error': str(e)})
        logger.error(f"Data export error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Failed to export project data"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)