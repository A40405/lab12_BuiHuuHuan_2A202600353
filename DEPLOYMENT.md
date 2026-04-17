# Deployment Information — Lab 6 Production AI Agent

## Public URL (After Deployment)

```
🚀 Railway: https://your-agent-name.railway.app
or
🚀 Render: https://your-agent-name.onrender.com
```

**Status:** Ready for deployment (local development complete)

---

## Platform Selection

| Platform | Pros | Cons | Time |
|----------|------|------|------|
| **Railway** | Easiest, auto-deploy, free tier | No free tier after trial | 5 min |
| **Render** | Free tier, GitHub integration | Cold starts on free | 10 min |
| **Cloud Run** | Scalable, pay-per-use | More config needed | 15 min |

**Recommended:** Railway for ease, Render for free tier

---

## Local Testing (Before Deployment)

### 1. Start Local Server

```bash
cd 06-lab-complete

# Setup
cp .env.example .env

# Run with Docker Compose (recommended)
docker compose up

# OR run directly with Python
python -c "
import sys
sys.path.insert(0, '.')
from app.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

### 2. Health Check

```bash
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "ok",
#   "version": "1.0.0",
#   "environment": "development",
#   "uptime_seconds": 2.345,
#   "total_requests": 1,
#   "timestamp": "2026-04-17T22:45:00.123456+00:00"
# }
```

### 3. Authentication Required

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

# Expected response (401 Unauthorized):
# {"detail": "Invalid or missing API key. Include header: X-API-Key: <key>"}
```

### 4. API Test (with API Key)

```bash
# Get API key from .env
API_KEY=$(grep AGENT_API_KEY .env | cut -d= -f2)

# Test ask endpoint
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deployment?"}'

# Expected response (200 OK):
# {
#   "question": "What is deployment?",
#   "answer": "Deployment là quá trình đưa code từ máy bạn lên server...",
#   "model": "gpt-4o-mini",
#   "timestamp": "2026-04-17T22:45:30.123456+00:00"
# }
```

### 5. Rate Limiting Test

```bash
API_KEY=$(grep AGENT_API_KEY .env | cut -d= -f2)

# Send 15 requests rapidly
for i in {1..15}; do
  echo "Request $i:"
  curl -s -X POST http://localhost:8000/ask \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"Test $i\"}" | python -m json.tool
done

# Expected: First 10 requests return 200, requests 11-15 return 429 (Too Many Requests)
```

### 6. Metrics Endpoint

```bash
API_KEY=$(grep AGENT_API_KEY .env | cut -d= -f2)

curl -s -X GET http://localhost:8000/metrics \
  -H "X-API-Key: $API_KEY" | python -m json.tool

# Expected response:
# {
#   "uptime_seconds": 45.2,
#   "total_requests": 21,
#   "error_count": 0,
#   "daily_cost_usd": 0.00001,
#   "daily_budget_usd": 5.0,
#   "budget_used_pct": 0.0
# }
```

### 7. Run Unit Tests

```bash
cd 06-lab-complete
python test_lab6.py

# Expected output:
# Testing Lab 6 endpoints...
# ✅ GET / : 200
# ✅ GET /health : 200
# ✅ GET /ready : 503
# ✅ POST /ask (no auth) : 401
# ✅ POST /ask (with auth) : 200
# ✅ GET /metrics (with auth) : 200
# ✅ ALL TESTS COMPLETED!
```

---

## Environment Variables Required

| Variable | Value | Required | Notes |
|----------|-------|----------|-------|
| `HOST` | `0.0.0.0` | Yes | Bind to all interfaces |
| `PORT` | `8000` | Yes | Application port |
| `ENVIRONMENT` | `production` | Yes | Set to "production" when deployed |
| `DEBUG` | `false` | Yes | Disable debug mode in prod |
| `AGENT_API_KEY` | (secret) | Yes | **CHANGE from default!** |
| `JWT_SECRET` | (secret) | Yes | **CHANGE from default!** |
| `REDIS_URL` | `redis://redis:6379` | Yes | Redis connection (local or managed) |
| `LOG_LEVEL` | `INFO` | No | Logging level (DEBUG/INFO/WARNING) |
| `DAILY_BUDGET_USD` | `5.0` | No | Per-user daily budget |
| `RATE_LIMIT_PER_MINUTE` | `20` | No | Requests per minute |

### Setting Secrets in Railway

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Project setup
cd 06-lab-complete
railway init

# 4. Set secrets
railway variables set AGENT_API_KEY="lab12_2A202600353_BuiHuuHuan"
railway variables set JWT_SECRET="lab12_2A202600353_BuiHuuHuan"

# 5. Deploy
railway up
```

### Setting Secrets in Render

1. Connect GitHub repository
2. Create Web Service → Connect repo
3. Select branch: `main`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Environment → Add secret:
   - `AGENT_API_KEY` = your-secret
   - `JWT_SECRET` = your-secret
7. Deploy!

---

## Deployment Checklist

### Code Quality
- [ ] All imports work (`python -c "from app.main import app"`)
- [ ] No hardcoded secrets in code
- [ ] `.env` file NOT committed (only `.env.example`)
- [ ] `__init__.py` exists in `app/` directory
- [ ] All test pass locally (`python test_lab6.py`)

### Configuration
- [ ] `app/config.py` reads from environment variables
- [ ] `.env.example` has all required variables
- [ ] `.dockerignore` excludes unnecessary files
- [ ] `requirements.txt` has all dependencies

### Docker
- [ ] `Dockerfile` uses multi-stage build
- [ ] Image builds successfully: `docker build -t agent .`
- [ ] Image size < 500 MB
- [ ] `docker compose up` starts both agent and Redis

### Security
- [ ] API Key validation enforced on `/ask`
- [ ] Rate limiting active (10 req/min for users)
- [ ] Cost guard enabled
- [ ] Security headers added (X-Content-Type-Options, X-Frame-Options)
- [ ] CORS properly configured
- [ ] No debug mode in production

### Health & Monitoring
- [ ] `/health` endpoint responds (200)
- [ ] `/ready` endpoint responds (200 when ready, 503 when starting)
- [ ] Graceful shutdown (SIGTERM) handled
- [ ] Structured JSON logging working
- [ ] `/metrics` endpoint shows usage stats

### API Endpoints
- [ ] `GET /` returns app info
- [ ] `GET /health` returns status
- [ ] `GET /ready` returns readiness
- [ ] `POST /ask` with auth returns response
- [ ] `POST /ask` without auth returns 401
- [ ] `GET /metrics` returns stats

---

## Pre-Deployment Verification

Run this script locally to verify everything:

```bash
cd 06-lab-complete

# Check 1: Imports
python -c "from app.main import app; print('✅ Imports OK')"

# Check 2: Config
python -c "from app.config import settings; print('✅ Config OK')"

# Check 3: Docker build
docker build -t test-agent . && echo "✅ Docker build OK"

# Check 4: Run tests
python test_lab6.py

# Check 5: File structure
test -f app/main.py && test -f app/config.py && test -f Dockerfile && \
  test -f docker-compose.yml && test -f requirements.txt && \
  echo "✅ All files present"

echo "
✅ Ready for deployment!
Next steps:
  1. railway init && railway up
  2. Copy public URL
  3. Update DEPLOYMENT.md with URL
  4. Test /health endpoint
"
```

---

## After Deployment

### Get Your Public URL

**Railway:**
```bash
railway domain
# Output: https://app-name-env.railway.app
```

**Render:**
- Check Render dashboard → Web Service → URL at top

### Update DEPLOYMENT.md

Replace template URLs with your actual URL:
```markdown
## Public URL
https://my-agent.railway.app  ← YOUR ACTUAL URL

## Test Commands
curl https://my-agent.railway.app/health
```

### Final Tests on Production

```bash
PROD_URL="https://your-actual-url.railway.app"
API_KEY="your-secret-key"

# 1. Health
curl $PROD_URL/health

# 2. API without auth (should fail)
curl -X POST $PROD_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

# 3. API with auth (should work)
curl -X POST $PROD_URL/ask \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

# 4. Rate limit test
for i in {1..15}; do
  curl -s -X POST $PROD_URL/ask \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"question": "test"}' | grep -o '"status_code":[^,}]*'
done

echo "✅ Deployment successful!"
```

---

## Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Module Not Found

```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use full module path
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Redis Connection Error

```bash
# Check if Redis is running
docker ps | grep redis

# Or restart Docker Compose
docker compose down
docker compose up
```

### Environment Variables Not Loaded

```bash
# Check .env file exists
ls -la .env

# Verify variables loaded
python -c "from app.config import settings; print(settings.agent_api_key)"
```

---

## Screenshots (Add to `screenshots/` folder)

Create `screenshots/` directory and add:

```
screenshots/
├── health-check.png       # curl http://localhost:8000/health
├── api-test.png           # POST /ask with response
├── rate-limit-test.png    # 15 requests showing rate limit
├── railway-dashboard.png  # Railway deployment dashboard
├── render-deployed.png    # Render service running
└── metrics.png            # GET /metrics response
```

To capture screenshots:

```bash
# Copy response to file
curl http://localhost:8000/health | python -m json.tool > screenshots/health-response.txt

# Take screen capture
# macOS: Cmd+Shift+4
# Windows: Win+Shift+S
# Linux: gnome-screenshot
```

---

## Summary

✅ **Local Testing:** Complete  
⏳ **Deployment:** Ready to Railway/Render  
📊 **Monitoring:** Health + metrics endpoints  
🔒 **Security:** API Key + rate limiting  
💰 **Budget:** Cost guard enabled  
📈 **Scalability:** Docker + stateless design  

**Next Step:** Deploy to Railway or Render using instructions above!
