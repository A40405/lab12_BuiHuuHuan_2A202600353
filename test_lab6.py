#!/usr/bin/env python
"""Test all endpoints for Lab 6"""
import sys
import os
sys.path.insert(0, os.getcwd())

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("Testing Lab 6 endpoints...\n")

# 1. Root
r = client.get('/')
print(f'✅ GET / : {r.status_code}')
print(f'   App: {r.json().get("app")}')
print(f'   Version: {r.json().get("version")}\n')

# 2. Health
r = client.get('/health')
print(f'✅ GET /health : {r.status_code}')
data = r.json()
print(f'   Status: {data.get("status")}')
print(f'   Version: {data.get("version")}\n')

# 3. Ready
r = client.get('/ready')
print(f'✅ GET /ready : {r.status_code}')
print(f'   Ready: {r.json().get("ready")}\n')

# 4. Ask without API key (should fail 401)
r = client.post('/ask', json={'question': 'Hello'})
print(f'✅ POST /ask (no auth) : {r.status_code} (expected 401)')
print(f'   Error: {r.json().get("detail")}\n')

# 5. Ask with API key (should succeed)
r = client.post('/ask', 
    json={'question': 'What is deployment?'},
    headers={'X-API-Key': 'dev-key-change-me'}
)
print(f'✅ POST /ask (with auth) : {r.status_code}')
data = r.json()
print(f'   Question: {data.get("question")}')
print(f'   Answer (truncated): {data.get("answer")[:60]}...')
print(f'   Model: {data.get("model")}\n')

# 6. Metrics (protected)
r = client.get('/metrics', headers={'X-API-Key': 'dev-key-change-me'})
print(f'✅ GET /metrics (with auth) : {r.status_code}')
data = r.json()
print(f'   Total requests: {data.get("total_requests")}')
print(f'   Error count: {data.get("error_count")}')
print(f'   Budget used: {data.get("budget_used_pct")}%\n')

# 7. Rate limit test
print('Testing rate limit (sending 15 requests)...')
api_key = 'dev-key-change-me'
success = 0
limited = 0
for i in range(15):
    r = client.post('/ask',
        json={'question': f'Test {i}'},
        headers={'X-API-Key': api_key}
    )
    if r.status_code == 200:
        success += 1
    elif r.status_code == 429:
        limited += 1
print(f'   Success: {success}/15')
print(f'   Rate limited: {limited}/15 (expected ~5 when limit=10)\n')

print('✅ ALL TESTS COMPLETED!')
