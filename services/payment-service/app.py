import os
import stripe
import psycopg2
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
DATABASE_URL = os.getenv('DATABASE_URL')
SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL')
CANCEL_URL = os.getenv('STRIPE_CANCEL_URL')

YOUR_PRODUCT_PRICE_ID = os.getenv('STRIPE_PRODUCT_PRICE_ID')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    project_id = data.get('project_id')

    if not project_id:
        return jsonify({"error": "project_id is required"}), 400
    
    if not YOUR_PRODUCT_PRICE_ID:
        app.logger.error("STRIPE_PRODUCT_PRICE_ID is not set.")
        return jsonify({"error": "Server configuration error: Product price ID is missing."}), 500

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': YOUR_PRODUCT_PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f'{SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=CANCEL_URL,
            client_reference_id=project_id,
            metadata={
                'project_id': project_id
            }
        )
        return jsonify({"checkout_url": checkout_session.url})
    except stripe.error.StripeError as e:
        app.logger.error(f"Error creating checkout session: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        app.logger.error(f"Invalid payload: {e}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        app.logger.error(f"Invalid signature: {e}")
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        project_id = session.get('client_reference_id')

        if project_id:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE projects SET status = %s WHERE id = %s",
                    ('paid', project_id)
                )
                conn.commit()
                cur.close()
                conn.close()
                app.logger.info(f"Project {project_id} status updated to 'paid'.")
            except Exception as e:
                app.logger.error(f"Database update failed for project {project_id}: {e}")
                # In a real application, you might want to retry or log this more robustly
                return jsonify({"error": "Database update failed"}), 500
        else:
            app.logger.warning(f"checkout.session.completed event received without client_reference_id: {session}")

    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']
        project_id = session.get('client_reference_id')
        app.logger.info(f"Async payment succeeded for project {project_id}.")
        # Handle post-payment fulfillment
    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        project_id = session.get('client_reference_id')
        app.logger.warning(f"Async payment failed for project {project_id}.")
        # Send email to user, etc.

    return jsonify(success=True)

@app.route("/health")
def health():
    # Basic health check, could be extended to check DB connection
    try:
        conn = get_db_connection()
        conn.close()
        return "OK", 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return "Database connection failed", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)