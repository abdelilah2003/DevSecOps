import requests
import os
import time

BASE = os.environ.get("BASE_URL", "http://localhost:5000")

def test_healthz():
    # Give the app a moment to start in some environments
    for _ in range(10):
        try:
            r = requests.get(f"{BASE}/healthz", timeout=2)
            assert r.status_code == 200
            assert r.json().get("status") == "ok"
            return
        except Exception:
            time.sleep(0.5)
    raise AssertionError("healthz endpoint did not respond OK")

def test_index():
    r = requests.get(f"{BASE}/", timeout=2)
    assert r.status_code == 200
    assert "message" in r.json()
