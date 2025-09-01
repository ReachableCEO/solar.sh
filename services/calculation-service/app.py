from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    # In a real application, you would process the LIDAR data
    # and run the solar simulation here.
    # For now, we'll just return a dummy project ID.
    project_id = "dummy_project_id"
    return jsonify({"project_id": project_id, "status": "processing"})

@app.route("/health")
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
