from flask import Flask, jsonify
from app_metrics import metrics_endpoint, track

app = Flask(__name__)

@app.get("/")
def index():
    return jsonify(message="Hello from Lab2!")

@app.get("/healthz")
def healthz():
    return jsonify(status="ok")

# Metrics
track(app)
metrics_endpoint(app)

if __name__ == "__main__":
    # Dev server; in Docker we use this too for simplicity
    app.run(host="0.0.0.0", port=5000, debug=False)
