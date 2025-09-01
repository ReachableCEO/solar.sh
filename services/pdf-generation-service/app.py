from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/download/<project_id>', methods=['GET'])
def download_pdf(project_id):
    # In a real application, you would retrieve the project data from the database,
    # generate a PDF, and return it as a file download.
    # For now, we'll just return a dummy message.
    return f"This would be a PDF for project {project_id}"

@app.route("/health")
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
