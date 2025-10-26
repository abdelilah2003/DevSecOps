from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from time import time
from flask import Response, request

REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency', ['endpoint', 'method'])
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['endpoint', 'method', 'status'])

def metrics_endpoint(app):
    @app.route('/metrics')
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def track(app):
    @app.before_request
    def _start_timer():
        request._start_time = time()

    @app.after_request
    def _record(resp):
        elapsed = time() - getattr(request, '_start_time', time())
        REQUEST_LATENCY.labels(request.endpoint or 'unknown', request.method).observe(elapsed)
        REQUEST_COUNT.labels(request.endpoint or 'unknown', request.method, resp.status_code).inc()
        return resp
