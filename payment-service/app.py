from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    project_id = data.get('project_id')
    # In a real application, you would create a Stripe checkout session here.
    # For now, we'll just return a dummy checkout URL.
    checkout_url = f"https://checkout.stripe.com/dummy_session_for_{project_id}"
    return jsonify({"checkout_url": checkout_url})

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    data = request.get_json()
    # In a real application, you would verify the webhook signature
    # and update the project status in the database.
    print(f"Received Stripe webhook: {data}")
    return jsonify({"status": "success"})

@app.route("/health")
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
