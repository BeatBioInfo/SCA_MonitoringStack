import time
import random
from flask import Flask, jsonify, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

app = Flask(__name__)

# Count every HTTP request, tagged by method, endpoint, and status code
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

# Measure how long each request takes
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

# Business metrics — the ones your manager actually cares about
PAYMENT_SUCCESS = Counter("payment_success_total", "Successful payments")
PAYMENT_FAILURE = Counter("payment_failure_total", "Failed payments")

# A simple "am I alive?" flag
APP_UP = Gauge("pay_api_up", "Whether pay-api is running")
APP_UP.set(1)

@app.route("/")
def home():
    start = time.time()
    REQUEST_COUNT.labels(method="GET", endpoint="/", status="200").inc()
    REQUEST_LATENCY.labels(method="GET", endpoint="/").observe(time.time() - start)
    return "<h1>Welcome to Pay-API</h1><p>Try /payment or /metrics</p>"

@app.route("/payment")
def payment():
    start = time.time()

    # Simulate real work: a request takes between 50ms and 500ms
    delay = random.uniform(0.05, 0.5)
    time.sleep(delay)

    # Simulate a 5% failure rate so we have interesting data to graph
    if random.random() < 0.05:
        PAYMENT_FAILURE.inc()
        REQUEST_COUNT.labels(method="GET", endpoint="/payment", status="500").inc()
        REQUEST_LATENCY.labels(method="GET", endpoint="/payment").observe(time.time() - start)
        return jsonify({"status": "error", "message": "payment failed"}), 500

    PAYMENT_SUCCESS.inc()
    REQUEST_COUNT.labels(method="GET", endpoint="/payment", status="200").inc()
    REQUEST_LATENCY.labels(method="GET", endpoint="/payment").observe(time.time() - start)
    return jsonify({"status": "success", "amount": round(random.uniform(10, 500), 2)})

@app.route("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()
    return jsonify({"status": "ok"})

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)