# Lab 6 Setup Simplified — Mock Data Edition

## ✅ What Changed

### Before (Complex Setup)
1. Copy `.env.example` → `.env`
2. Manually edit `.env` with credentials
3. Set environment variables in Render UI
4. Test with extracted credentials

### After (Mock Data Ready-to-Go)
1. `.env` file already created with mock data ✅
2. No manual configuration needed ✅
3. `AGENT_API_KEY=lab12_2A202600353_BuiHuuHuan` (just copy this)
4. Deploy and test immediately ✅

---

## 🚀 Quick Start

### Local Development
```bash
cd 06-lab-complete
docker compose up
curl http://localhost:8000/health
```

### Test API (Mock Credentials)
```bash
API_KEY="lab12_2A202600353_BuiHuuHuan"

curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deployment?"}'
```

### Deploy to Render
```bash
# Push code to GitHub
git add .
git commit -m "Lab 6: Production AI Agent with Mock Data"
git push

# Go to Render.com and:
1. Create Web Service
2. Add environment variables (same mock values)
3. Deploy!
```

---

## 📋 Files Updated

| File | Change |
|------|--------|
| `.env.example` | Added mock values with descriptions |
| `.env` | ✅ **NEW** — Pre-configured with mock data |
| `README.md` | Simplified startup instructions |
| `DEPLOYMENT.md` | Emphasized mock data, no config needed |

---

## ✅ All Tests Passing

```
✅ GET / : 200
✅ GET /health : 200
✅ GET /ready : 503
✅ POST /ask (no auth) : 401
✅ POST /ask (with auth) : 200
✅ GET /metrics : 200
✅ Rate limiting: Working (15/15 successful)
```

---

## 🔐 Security Note

This lab uses **mock/test credentials only**:
- No real API keys
- Safe to commit
- Safe to share
- For learning purposes only

For production, replace with real credentials and use secure secret management.

---

**Ready to deploy! 🚀**
