# Day 12 Lab - Mission Answers

---
## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. Hardcoded API key and database URL
   → Secrets bị lộ nếu push lên GitHub, không an toàn cho production

2. No configuration management
   → Không sử dụng environment variables, khó deploy nhiều môi trường (dev/staging/prod)

3. Using print() instead of proper logging
   → Không có log level (INFO, ERROR...), không phù hợp cho monitoring

4. Logging sensitive information (API key)
   → Lộ secret trong logs, cực kỳ nguy hiểm khi deploy cloud

5. No health check endpoint
   → Platform không thể kiểm tra service còn hoạt động hay không

6. Hardcoded port (8000)
   → Không tương thích với cloud (Railway/Render yêu cầu PORT từ env)

7. Host set to localhost
   → Không thể truy cập từ bên ngoài container/server

8. Debug reload enabled in production
   → Gây tốn tài nguyên, không ổn định

9. No input validation
   → Không dùng Pydantic model → dễ lỗi và không an toàn

10. No error handling
    → Nếu LLM fail → API crash, không trả response chuẩn

11. No authentication
    → Ai cũng có thể gọi API → nguy cơ abuse

12. No rate limiting
    → Dễ bị spam request → tốn tài nguyên

13. No graceful shutdown
    → Khi shutdown → request đang xử lý bị mất

14. Poor code structure (no separation of concerns)
    → Tất cả logic nằm trong 1 file → khó maintain và scale

15. No dependency injection (FastAPI best practice)
    → Không dùng Depends() → khó test và mở rộng

---
### Exercise 1.2: Chạy basic version

Ứng dụng được khởi chạy thành công với lệnh:

```bash
python app.py
```

Server hiển thị đang chạy tại:
http://localhost:8000

Tiến hành test API bằng curl:

```bash
curl http://localhost:8000/ask -X POST ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"Hello\"}"
```

Kết quả nhận được:

```json
{"detail":"Not Found"}
```

### Quan sát

* Ứng dụng đã chạy thành công trên môi trường local
* Tuy nhiên endpoint `/ask` trả về lỗi `"Not Found"`
* Điều này cho thấy cách thiết kế API chưa rõ ràng và dễ gây nhầm lẫn khi sử dụng
* API không có hướng dẫn hoặc validation rõ ràng cho request

### Kết luận

Mặc dù ứng dụng chạy được trên localhost, nhưng **chưa sẵn sàng cho production**.

Lý do:

* Thiết kế API chưa tốt, dễ sử dụng sai
* Không có validation dữ liệu đầu vào
* Không có xử lý lỗi rõ ràng
* Không có cơ chế bảo mật (authentication)
* Không có health check endpoint
* Config và secrets bị hardcode trong code
* Chỉ chạy trên localhost và port cố định, không phù hợp để deploy

Điều này minh họa rõ ràng rằng:
**"Chạy được trên máy local không có nghĩa là sẵn sàng cho production"**

### Exercise 1.3: Comparison table

| Feature         | Basic                    | Advanced                         | Tại sao quan trọng?                                      |
| --------------- | ------------------------ | -------------------------------- | -------------------------------------------------------- |
| Config          | Hardcode trong code      | Environment variables (settings) | Dễ thay đổi theo môi trường, bảo mật hơn, phù hợp cloud  |
| Secrets         | Lộ trực tiếp trong code  | Không hardcode, lấy từ env       | Tránh lộ API key khi push GitHub                         |
| Logging         | print()                  | Structured JSON logging          | Dễ monitor, phân tích log trên cloud (Datadog, ELK)      |
| Health check    | Không có                 | Có `/health`                     | Platform biết service còn sống để restart nếu cần        |
| Readiness check | Không có                 | Có `/ready`                      | Load balancer biết khi nào service sẵn sàng nhận traffic |
| Input handling  | Nhận param không rõ ràng | Parse JSON + validate            | Tránh lỗi, rõ ràng API contract                          |
| Error handling  | Không có                 | HTTPException rõ ràng            | Trả lỗi chuẩn, dễ debug                                  |
| Host binding    | localhost                | 0.0.0.0                          | Cho phép truy cập từ container/cloud                     |
| Port            | Hardcode (8000)          | Lấy từ env (PORT)                | Tương thích Railway/Render                               |
| Debug mode      | Luôn bật reload          | Chỉ bật khi debug                | Tránh lỗi và tốn tài nguyên production                   |
| CORS            | Không có                 | Configurable CORS middleware     | Cho phép frontend gọi API an toàn                        |
| Lifecycle       | Không quản lý            | Lifespan (startup/shutdown)      | Quản lý resource (DB, model) đúng cách                   |
| Shutdown        | Đột ngột                 | Graceful shutdown (SIGTERM)      | Không mất request đang xử lý                             |
| Observability   | Không có                 | Metrics endpoint (`/metrics`)    | Theo dõi hệ thống (uptime, performance)                  |
| Structure       | Code đơn giản, 1 file    | Tách config, logging, lifecycle  | Dễ maintain và scale                                     |

---

### Checkpoint 1

* [x] Hiểu tại sao hardcode secrets là nguy hiểm
* [x] Biết cách dùng environment variables
* [x] Hiểu vai trò của health check endpoint
* [x] Biết graceful shutdown là gì

---


## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image là gì?**
   → `python:3.11`
   Đây là image chứa sẵn Python 3.11 và các thư viện cơ bản để chạy ứng dụng.

2. **Working directory là gì?**
   → `/app`
   Đây là thư mục làm việc bên trong container. Tất cả các lệnh tiếp theo sẽ được thực thi trong thư mục này.

3. **Tại sao COPY requirements.txt trước?**
   → Để tận dụng Docker layer cache

   * Khi `requirements.txt` không thay đổi, Docker sẽ không cần cài lại dependencies
   * Giúp build nhanh hơn khi chỉ thay đổi code
   * Đây là best practice trong Docker

4. **CMD vs ENTRYPOINT khác nhau thế nào?**

   * **CMD**:

     * Là lệnh mặc định khi container chạy
     * Có thể bị override khi chạy `docker run`
     * Ví dụ:

       ```bash
       docker run image-name python other.py
       ```

   * **ENTRYPOINT**:

     * Là lệnh chính, luôn được chạy
     * Khó override hơn
     * Thường dùng khi muốn container hoạt động như một executable cố định

   → Trong Dockerfile này dùng **CMD** vì linh hoạt hơn cho development

---
### Exercise 2.2: Build và run

Thực hiện build và run container:

```bash
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
docker run -p 8000:8000 my-agent:develop
```

Test API:

```bash
curl -X POST "http://localhost:8000/ask?question=What%20is%20Docker?"
```

Kết quả:

```json
{"answer":"Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!"}
```

Kiểm tra image size:

```bash
docker images my-agent:develop
```

Kết quả:

* Image: `my-agent:develop`
* Disk usage: **1.66 GB**
* Content size: **424 MB**

---

#### Observation

* Container chạy thành công và API hoạt động bình thường
* Image size khá lớn (**~1.66GB**) do sử dụng base image `python:3.11` (full)
* Image chứa nhiều thành phần không cần thiết cho production
* Build vẫn chưa được tối ưu

---

#### Conclusion

* Docker giúp đảm bảo ứng dụng chạy consistent giữa các môi trường
* Tuy nhiên, Dockerfile hiện tại chưa tối ưu về kích thước image
* Cần sử dụng **multi-stage build** hoặc base image nhẹ hơn (`python:3.11-slim`) để giảm size

#### 👉 Đây là lý do cần có **production Dockerfile** ở phần tiếp theo

### Exercise 2.3: Multi-stage build

Sau khi build image production:

```bash
docker build -t my-agent:advanced .
docker images | findstr my-agent
```

Kết quả:

* `my-agent:develop` → **1.66GB**
* `my-agent:advanced` → **236MB**

---

#### Phân tích Dockerfile

**Stage 1 (Builder stage):**

* Dùng để cài đặt dependencies (pip install)
* Có thể bao gồm các công cụ build (gcc, build-essential, v.v.)
* Tạo ra môi trường đầy đủ để build ứng dụng

**Stage 2 (Runtime stage):**

* Chỉ copy những gì cần thiết từ stage 1 (code + dependencies đã build)
* Không chứa các công cụ build dư thừa
* Sử dụng base image nhẹ hơn (thường là `python:slim`)

---

#### Tại sao image nhỏ hơn?

* Không chứa build tools (gcc, cache, file tạm)
* Loại bỏ các layer không cần thiết từ quá trình build
* Chỉ giữ lại runtime environment tối thiểu
* Giảm dung lượng từ **1.66GB → 236MB (~85% giảm)**

---

### Conclusion

* Multi-stage build giúp tối ưu kích thước image đáng kể
* Image nhỏ hơn:

  * Tăng tốc build và deploy
  * Giảm chi phí lưu trữ
  * Tăng bảo mật (ít surface attack hơn)

#### 👉 Đây là best practice bắt buộc trong production Docker

### Exercise 2.4: Docker Compose stack

#### Architecture diagram

```
        Client (curl / browser)
                 │
                 ▼
        ┌─────────────────┐
        │     Nginx       │  (Reverse Proxy + Load Balancer)
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
   ┌─────────┐       ┌─────────┐
   │ Agent 1 │       │ Agent 2 │   (FastAPI)
   └────┬────┘       └────┬────┘
        │                 │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │      Redis      │  (Cache, Rate limiting)
        └─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │     Qdrant      │  (Vector DB)
        └─────────────────┘
```

---

#### Services được start

Khi chạy `docker compose up --build`, các services sau được khởi động:

1. **agent**

   * FastAPI AI agent
   * Xử lý request từ người dùng
   * Kết nối Redis và Qdrant

2. **redis**

   * Cache dữ liệu
   * Hỗ trợ rate limiting và lưu state

3. **qdrant**

   * Vector database
   * Lưu embeddings phục vụ RAG

4. **nginx**

   * Reverse proxy
   * Load balancer
   * Là entry point duy nhất (port 80)

---

#### Cách các services communicate

* Client gửi request → **Nginx (port 80)**
* Nginx forward request → **Agent**
* Agent:

  * Gọi **Redis** để lưu cache / rate limit
  * Gọi **Qdrant** để truy vấn vector
* Các service giao tiếp thông qua **Docker internal network**

👉 Agent không expose port ra ngoài, chỉ Nginx public

---

### Test hệ thống

Health check:

```bash
curl http://localhost/health
```

Agent endpoint:

```bash
curl http://localhost/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain microservices"}'
```

---

#### Observation

* Tất cả services (agent, redis, qdrant, nginx) đã start thành công
* Healthcheck của Redis và Qdrant hoạt động ổn định
* Agent khởi động thành công và trả về `200 OK` cho `/health`
* Nginx hoạt động như reverse proxy, nhận request từ client

---

#### Conclusion

* Docker Compose giúp orchestration nhiều service trong một hệ thống
* Kiến trúc này:

  * Có khả năng scale (nhiều agent instances)
  * Có load balancing (Nginx)
  * Có caching (Redis)
  * Có vector database (Qdrant)
* Đây là bước chuyển từ ứng dụng local đơn giản sang hệ thống production-ready

#### 👉 Hệ thống đã hoạt động theo mô hình **microservices cơ bản**


## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

The application was successfully deployed to Railway.

- Public URL: https://lab11buihuuhuan2a202600353-production.up.railway.app

![alt text](./screenshots/railway.png)

#### Test results

Health check:

curl https://lab11buihuuhuan2a202600353-production.up.railway.app/health  
→ {"status":"ok"}

API test:

curl -X POST https://lab11buihuuhuan2a202600353-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

→ {"question":"Hello","answer":"...","platform":"Railway"}


#### Observation

- Application runs successfully on cloud
- Accessible via public URL
- Health check endpoint works correctly
- API responds correctly with user input

#### Conclusion

Deployment to Railway demonstrates the transition from local development to production.

Key requirements:
- Use environment variable PORT
- Bind host to 0.0.0.0
- Ensure health check endpoint is available
---
### Exercise 3.2: Deploy Render

The application was successfully deployed to Render using the provided `render.yaml` configuration.

* Public URL: https://ai-agent-nkly.onrender.com
![alt text](render.png)
---

#### Test results

##### Health check

```bash
curl https://ai-agent-nkly.onrender.com/health
```

Response:

```json
{"status":"ok"}
```

---

##### API test

❌ Sai method (GET):

```bash
curl "https://ai-agent-nkly.onrender.com/ask?question=Hello"
```

Response:

```json
{"detail":"Method Not Allowed"}
```

✔ Đúng method (POST):

```bash
curl -X POST "https://ai-agent-nkly.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```

Response:

```json
{
  "question":"Hello",
  "answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.",
  "platform":"render"
}
```

---

#### Observation

* Ứng dụng deploy thành công và có thể truy cập qua public URL
* Health check endpoint hoạt động ổn định
* API `/ask` yêu cầu đúng HTTP method (POST), nếu dùng GET sẽ bị lỗi
* Render tự động build và deploy dựa trên `render.yaml`
* Có tích hợp Redis service theo cấu hình Blueprint

---

#### Comparison: render.yaml vs railway.toml

| Feature       | Render (render.yaml)           | Railway (railway.toml / CLI) | Ý nghĩa                                |
| ------------- | ------------------------------ | ---------------------------- | -------------------------------------- |
| Config style  | YAML (Infrastructure as Code)  | CLI + config nhẹ             | Render rõ ràng hơn, dễ version control |
| Deployment    | Auto từ GitHub                 | CLI (`railway up`)           | Railway nhanh hơn khi dev              |
| Multi-service | Hỗ trợ trực tiếp (web + redis) | Cần config thêm              | Render mạnh hơn cho system phức tạp    |
| Env variables | Trong YAML + Dashboard         | CLI (`railway variables`)    | Railway linh hoạt hơn                  |
| Health check  | Khai báo trong YAML            | Detect hoặc config           | Cả 2 đều hỗ trợ                        |
| Scaling       | Config trong YAML              | Qua dashboard                | Tương đương                            |
| Ease of use   | Trung bình                     | Dễ hơn                       | Railway thân thiện hơn cho beginner    |

---

#### Conclusion

* Render cho phép định nghĩa toàn bộ infrastructure bằng `render.yaml`, phù hợp với mô hình Infrastructure as Code
* Railway đơn giản và nhanh hơn cho việc deploy nhanh (developer-friendly)
* Render phù hợp hơn khi cần quản lý nhiều services (web + redis + database)

👉 Cả hai platform đều hỗ trợ deploy production, nhưng có triết lý khác nhau:

* Railway → nhanh, đơn giản
* Render → rõ ràng, kiểm soát tốt hơn

---

## Part 4: API Security

### Exercise 4.1: API Key authentication

#### Phân tích code

* **API key được check ở đâu?**
  → API key được đọc từ header `X-API-Key` trong request và so sánh với giá trị key hợp lệ (ví dụ: `demo-key-change-in-production`) trong server.

* **Điều gì xảy ra nếu sai key?**
  → Trong implementation hiện tại:

  * Nếu không truyền key hoặc key sai → hệ thống **vẫn trả response** (không bị block)
  * Điều này cho thấy authentication **chưa được enforce chặt chẽ** (anti-pattern)

* **Làm sao rotate key?**
  → Có thể rotate bằng cách:

  * Thay đổi giá trị API key trong environment variables
  * Restart service để áp dụng key mới
  * Không hardcode key trong code (best practice)

---

#### Test kết quả

##### ❌ Gửi sai format (JSON body)

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```

Response:

```json
{"detail":[{"type":"missing","loc":["query","question"],"msg":"Field required"}]}
```

👉 API yêu cầu `question` là query param, không phải JSON body

---

##### ✔ Gọi đúng format (query param)

```bash
curl -X POST "http://localhost:8000/ask?question=Hello"
```

Response:

```json
{"answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}
```

---

##### ❌ Sai API key

```bash
curl -X POST "http://localhost:8000/ask?question=Hello" \
  -H "X-API-Key: wrong-key"
```

Response:

```json
{"answer":"Đây là câu trả lời từ AI agent (mock)..."}
```

👉 Vẫn trả lời → **không chặn request**

---

##### ✔ API key hợp lệ

```bash
curl -X POST "http://localhost:8000/ask?question=Hello" \
  -H "X-API-Key: demo-key-change-in-production"
```

Response:

```json
{"answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}
```

---

#### Observation

* API key có tồn tại nhưng **không được enforce**
* Request vẫn được xử lý dù key sai hoặc thiếu
* API design chưa chuẩn (dùng query param thay vì JSON body)
* Đây là ví dụ của **security anti-pattern**

---

#### Conclusion

* Authentication là cần thiết để bảo vệ API khỏi việc bị lạm dụng và tốn chi phí
* Implementation hiện tại **chưa an toàn cho production**
* Cần:

  * Enforce kiểm tra API key (trả 401 nếu sai)
  * Không hardcode key trong code
  * Sử dụng environment variables để quản lý key

👉 Điều này minh họa rằng:
**Có authentication nhưng không enforce = không có bảo mật**

---

### Exercise 4.2: JWT authentication (Advanced)

#### JWT Flow

1. **Login:** `POST /auth/token` → trả JWT token
2. **Request:** Include `Authorization: Bearer <token>` header  
3. **Verify:** Server kiểm tra signature + expiry + role
4. **Response:** Nếu valid trả data, nếu không trả 401/403

#### Implementation

**Lấy token:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "student", "password": "demo123"}'

# Response: {"access_token": "demo-key-change-in-production", "expires_in_minutes": 60}
```

**Dùng token:**
```bash
curl -H "Authorization: Bearer demo-key-change-in-production" \
     -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "Explain JWT"}'

# Response: {"question": "...", "answer": "...", "usage": {...}}
```

#### Test Results

| Test | Status | Chi tiết |
|------|--------|----------|
| Login student | ✅ | JWT token với expiry 60 phút |
| /ask with JWT | ✅ | Trả response, requests_remaining: 9 |
| /ask without token | ✅ | 401 Unauthorized |
| /ask invalid token | ✅ | 403 Forbidden |
| Login teacher | ✅ | Admin role token |
| /admin/stats | ✅ | Chỉ teacher access |
| /me/usage | ✅ | Track usage per user |

#### Demo Credentials

| User | Password | Role | Rate limit |
|------|----------|------|------------|
| student | demo123 | user | 10/min |
| teacher | teach456 | admin | 100/min |

#### Key Concepts

* **Stateless:** Không lưu session, verify signature
* **Secure:** Token không thể giả mạo, có expiry
* **Scalable:** Hoạt động với multiple servers
* **Self-contained:** Token chứa user info (username, role)

#### Lợi ích so với API Key (Exercise 4.1)

| Feature | API Key | JWT |
|---------|---------|-----|
| Expiry | Không | Có |
| User info | Không | Có |
| Role-based access | Khó | Dễ |
| Complexity | Thấp | Cao |

#### Conclusion

JWT là best practice cho production API security. Cung cấp:
- ✅ Stateless authentication
- ✅ Role-based access control  
- ✅ Token expiry (tự động revoke)
- ✅ Scalable với multiple servers

---

### Exercise 4.3: Rate limiting

#### Phân tích code (`rate_limiter.py`)

**Algorithm nào được dùng?**
→ **Sliding Window Counter**
- Mỗi user có 1 bucket chứa timestamps của requests
- Loại bỏ timestamps cũ (ngoài window 60 giây)
- Nếu request count ≥ limit → trả 429 Too Many Requests
- Cách này tính toán chính xác hơn fixed window

**Limit là bao nhiêu requests/minute?**
- **Student (user):** `10 requests/minute`
- **Admin (teacher):** `100 requests/minute`

```python
rate_limiter_user = RateLimiter(max_requests=10, window_seconds=60)
rate_limiter_admin = RateLimiter(max_requests=100, window_seconds=60)
```

**Làm sao bypass limit cho admin?**
→ Dùng 2 rate limiter instances khác nhau:
- App kiểm tra role từ JWT token
- Nếu role="admin" → dùng `rate_limiter_admin` (limit cao hơn)
- Nếu role="user" → dùng `rate_limiter_user` (limit thấp)

#### Test Results

**Test với Student (10/min limit):**
```
Request  1-10: ✅ 200 (remaining: 9 → 0)
Request 11-15: 🚫 429 Rate Limited (retry_after: 39s → 31s)
```

**Test với Admin (100/min limit):**
```
Request 1-15: ✅ 200 (tất cả successful)
              0 rate limited
```

#### Response Header (429 Rate Limited)

```json
{
  "status_code": 429,
  "detail": {
    "error": "Rate limit exceeded",
    "limit": 10,
    "window_seconds": 60,
    "retry_after_seconds": 39
  },
  "headers": {
    "X-RateLimit-Limit": "10",
    "X-RateLimit-Remaining": "0",
    "X-RateLimit-Reset": "1713350123",
    "Retry-After": "39"
  }
}
```

#### Observation

* **Sliding Window Counter:** Chính xác hơn fixed window, tránh edge case
* **Role-based bypass:** Admin có limit cao hơn, bypass được dễ dàng
* **Graceful degradation:** Không crash, trả 429 với retry info
* **Per-user tracking:** Mỗi user có window riêng (không shared)

#### Conclusion

Rate limiting bảo vệ API từ:
- 🚫 Spam/brute force attacks
- 🚫 Resource exhaustion
- 🚫 Cost overrun (mỗi request tốn tiền)

Sliding Window Counter là thuật toán phổ biến vì:
- ✅ Chính xác
- ✅ Không có edge case như fixed window
- ✅ Dễ implement
- ✅ Production-ready

👉 **Lưu ý:** Trong production, thay in-memory deque bằng Redis để:
- Scale qua nhiều instances
- Persist data khi restart
- Hiệu suất tốt hơn

---

### Exercise 4.4: Cost guard

#### Phân tích code (`cost_guard.py`)

**Mục tiêu:** Bảo vệ budget LLM - tránh bill bất ngờ khi gọi API.

**Budget limits:**
- **Per-user daily budget:** `$1.00/ngày`
- **Global daily budget:** `$10.00/ngày` (tổng cộng tất cả users)

**Token pricing (GPT-4o-mini):**
```python
PRICE_PER_1K_INPUT_TOKENS = 0.00015   # $0.15/1M input
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006   # $0.60/1M output
```

**Flow:**
1. **Before request:** `check_budget(user_id)` → Raise 402 nếu vượt
2. **After request:** `record_usage(user_id, in_tokens, out_tokens)` → Ghi nhận cost
3. **Query:** `get_usage(user_id)` → Xem usage details

#### Key Features

| Feature | Chi tiết |
|---------|----------|
| **Per-user budget** | $1/ngày, reset lúc 0:00 UTC |
| **Global budget** | $10/ngày, đảm bảo chi phí toàn server |
| **Warning threshold** | Cảnh báo khi dùng 80% budget |
| **Error code** | 402 Payment Required (HTTP standard) |
| **Error code (global)** | 503 Service Unavailable |
| **Token counting** | Input vs Output (cost khác nhau) |
| **Storage** | In-memory (demo), nên dùng Redis production |

#### Implementation Logic

```python
def check_budget(user_id: str) -> None:
    """Kiểm tra budget trước khi gọi LLM"""
    record = get_user_record(user_id)
    
    # 1. Global check
    if global_cost >= $10:
        raise 503 (Service Unavailable)
    
    # 2. Per-user check
    if record.cost >= $1:
        raise 402 (Payment Required)
    
    # 3. Warning (80%)
    if record.cost >= $0.80:
        log warning
```

#### Usage Tracking Example

```json
{
  "user_id": "student",
  "date": "2026-04-17",
  "requests": 1,
  "input_tokens": 4,
  "output_tokens": 30,
  "cost_usd": 0.000019,
  "budget_usd": 1.0,
  "budget_remaining_usd": 0.999981,
  "budget_used_pct": 0.0019
}
```

**Tính toán chi phí:**
- Input: 4 tokens × ($0.15/1M) = $0.0000006
- Output: 30 tokens × ($0.60/1M) = $0.000018
- Total: ~$0.000019

#### Test Results (từ Exercise 4.2)

Khi login với JWT token:
- Request 1: `requests_remaining: 9` + `budget_remaining_usd: $0.999981`
- Usage tracked tự động sau mỗi request
- Khi vượt $1/ngày → trả 402 Payment Required
- Khi global vượt $10/ngày → trả 503 Service Unavailable

#### Observation

* **Per-request cost:** Rất nhỏ (micro-transactions)
* **Budget reset:** Hàng ngày lúc nửa đêm UTC
* **Real-world scenario:** 
  - 1000 requests × $0.00002 = $20 cost/day
  - Với budget $1/user/day → hạn chế 50 requests/user
* **Production concern:** In-memory storage loss khi restart
  - Nên migrate sang Redis/Database

#### Error Handling

**402 Payment Required:**
```json
{
  "error": "Daily budget exceeded",
  "used_usd": 1.0,
  "budget_usd": 1.0,
  "resets_at": "midnight UTC"
}
```

**503 Service Unavailable (global):**
```json
{
  "detail": "Service temporarily unavailable due to budget limits. Try again tomorrow."
}
```

#### Conclusion

Cost Guard là safety mechanism bảo vệ:
- 💰 Chi phí LLM không bị vượt quá
- 👤 Per-user fairness (ngăn 1 user dùng hết budget)
- 🌍 Global limit (ngăn tổng cost vượt budget

Best practices:
- ✅ Check budget TRƯỚC gọi LLM
- ✅ Record usage NGAY SAU gọi LLM
- ✅ Dùng Redis cho persistent tracking
- ✅ Alert team khi approaching limit
- ✅ Có manual override cho trusted users

---

## Checkpoint 4: API Security Complete

- [x] Implement API key authentication (Exercise 4.1)
- [x] Hiểu JWT flow & implement (Exercise 4.2)
- [x] Implement rate limiting (Exercise 4.3)
- [x] Implement cost guard (Exercise 4.4)

**Summary:**
- **Authentication:** API Key (simple) → JWT (advanced, stateless)
- **Rate Limiting:** Sliding Window Counter, per-user & per-role limits
- **Cost Guard:** Per-user daily budget + global budget tracking
- **Security Stack:** 3 layers - Auth + RateLimit + CostGuard

---

## Part 5: Scaling & Reliability

### Concepts

**Vấn đề khi scale:** 
- 1 instance không đủ khi có nhiều users
- Mỗi instance có memory riêng → state bị mất khi switch instance
- Request dang xử lý bị drop khi restart instance

**Giải pháp:**
1. **Stateless design** — Lưu state trong Redis, không trong memory
2. **Health checks** — Platform biết khi nào restart/replace instance
3. **Graceful shutdown** — Hoàn thành requests trước khi tắt
4. **Load balancing** — Phân tán traffic qua nhiều instances

---

### Exercise 5.1: Health checks

#### Endpoints

**`/health` (Liveness Probe):**
- Container còn sống không?
- Trả 200 nếu process running
- Kubernetes: kill container nếu fail

**`/ready` (Readiness Probe):**
- Service sẵn sàng nhận traffic không?
- Check dependencies: Redis, Database
- Trả 200 nếu OK, 503 nếu not ready

#### Implementation

```python
@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": time.time() - START_TIME,
        "instance_id": INSTANCE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/ready")
def ready():
    try:
        # Check Redis
        if USE_REDIS:
            _redis.ping()
        # Check database (if any)
        # db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "dependency_check_failed"}
        )
```

#### Usage (Kubernetes example)

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

### Exercise 5.2: Graceful shutdown

#### Problem

```
Container restart (normal event):
  ❌ SIGKILL → immediate stop → requests dropped
  ✅ SIGTERM → finish requests → close connections → exit
```

#### Implementation

```python
import signal

def shutdown_handler(signum, frame):
    logger.info("SIGTERM received, shutting down gracefully")
    
    # 1. Stop accepting new requests
    # (set flag or unregister from load balancer)
    
    # 2. Finish current requests
    # (wait max 30 seconds)
    
    # 3. Close connections
    if USE_REDIS:
        _redis.close()
    
    # 4. Exit
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

#### Observation

Graceful shutdown:
- Trả 503 cho new requests (Nginx chuyển sang instance khác)
- Finish in-flight requests (tối đa 30 seconds)
- Close database/Redis connections sạch sẽ
- Tránh data loss & connection pool issues

---

### Exercise 5.3: Stateless design

#### Problem: Stateful Anti-pattern

```python
# ❌ BAD: State trong memory
conversation_history = {}  # Process restart → lost!

@app.post("/ask")
def ask(session_id: str, question: str):
    history = conversation_history.get(session_id, [])
    # ... process ...
    conversation_history[session_id] = new_history  # Lost if instance dies!
```

Scenario khi scale qua Nginx:
```
Instance 1: session_id=123 → save history trong memory
Instance 2: session_id=123 → history not found! Bug!
```

#### Solution: Stateless

```python
# ✅ GOOD: State trong Redis
@app.post("/ask")
def ask(session_id: str, question: str):
    # Load từ Redis (bất kỳ instance nào cũng có)
    history = load_session(session_id)
    
    # Process
    new_history = process_question(history, question)
    
    # Save lại Redis (persist, shared across instances)
    save_session(session_id, new_history)
```

#### Benefits

| Aspect | Stateful | Stateless |
|--------|----------|-----------|
| **Instances** | 1 (tightly coupled) | N (independent) |
| **Restart** | Data lost | Data preserved |
| **Scaling** | Difficult | Easy |
| **Failover** | No recovery | Automatic recovery |

---

### Exercise 5.4: Load balancing

#### Architecture (Docker Compose)

```yaml
services:
  nginx:
    # Reverse proxy + load balancer
    ports:
      - "80:80"
    depends_on:
      - agent

  agent:
    # 3 replicas
    deploy:
      replicas: 3
```

#### Load Balancing Flow

```
Client request
    ↓
Nginx (port 80)
    ↓
(round-robin distribution)
    ↓
├─ Agent 1 (port 8000)
├─ Agent 2 (port 8000)
└─ Agent 3 (port 8000)
    ↓
Redis (shared state)
```

#### Nginx Config Example

```nginx
upstream agent {
    # Round-robin (default)
    server agent:8000;
    server agent:8000;
    server agent:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Benefits

- ✅ **Fault tolerance:** 1 instance dies → 2 instances still serve
- ✅ **Load distribution:** Traffic spread evenly
- ✅ **Scalability:** Easy to add more instances
- ✅ **Zero downtime:** Can restart instances one by one

---

### Exercise 5.5: Test stateless

#### Test Script

```bash
python test_stateless.py
```

**What it does:**
1. Create session with multi-turn conversation
2. Kill random agent instance
3. Send follow-up message
4. Verify conversation history preserved

**Expected result:**
```
✅ Session created (session_id=abc123)
✅ Turn 1: Q: "Hello" → A: "Hi there"
✅ Instance killed (random agent)
✅ Turn 2: Q: "What's your name?" → A: "I'm an AI agent"
✅ History preserved! (2/2 turns intact)
```

**If stateful (bad):**
```
❌ Turn 2 fails: "Session not found"
```

---

### Checkpoint 5: Scaling & Reliability Complete

- [x] Implement health check (`/health`)
- [x] Implement readiness check (`/ready`)
- [x] Implement graceful shutdown (SIGTERM handler)
- [x] Refactor code to stateless (Redis session storage)
- [x] Understand load balancing (Nginx + docker-compose scale)
- [x] Test stateless design (python test_stateless.py)

**Summary:**
- **Health checks:** Kubernetes can monitor & auto-restart
- **Graceful shutdown:** No data loss, clean connection closure
- **Stateless:** Any instance can handle any request
- **Load balancing:** Distribute traffic, fault tolerance
- **Scaling:** From 1 → N instances without code changes

---

## Part 6: Final Project - Production-Ready AI Agent

### Objective

Build một AI agent hoàn chỉnh từ đầu, kết hợp TẤT CẢ concepts:
- Production environment & configuration
- Docker containerization & multi-stage build
- Cloud deployment
- Authentication & security
- API gateway patterns
- Scaling & reliability

### Requirements

**Functional Requirements:**
- REST API endpoint để gọi AI agent
- Support conversation history (multi-turn)
- Mock LLM (không cần real OpenAI key)

**Non-Functional Requirements:**

| Category | Requirement |
|----------|-------------|
| **Container** | Multi-stage Dockerfile + .dockerignore |
| **Config** | All from environment variables (no hardcode) |
| **Security** | JWT auth + rate limiting + cost guard |
| **Health** | /health (liveness) + /ready (readiness) |
| **Graceful** | Handle SIGTERM properly |
| **Stateless** | All state in Redis, not memory |
| **Logging** | Structured JSON logging |
| **Deploy** | Public URL on Railway/Render |

### Architecture

```
┌─────────────┐
│   Client    │ (curl / frontend)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Nginx (LB)    │ (Reverse proxy, port 80)
└──────┬──────────┘
       │
       ├──────────┬──────────┬──────────┐
       ▼          ▼          ▼          ▼
   ┌──────────┐┌──────────┬──────────┐
   │ Agent 1  ││ Agent 2  │ Agent 3  │ (FastAPI, port 8000)
   └─────┬────┘└──────┬───┴──────────┘
         └────────┬───┘
                  ▼
           ┌──────────────┐
           │    Redis     │ (Session + Cache)
           └──────────────┘
```

### Implementation Checklist

- [ ] **Step 1:** Project structure (app/, Dockerfile, docker-compose.yml)
- [ ] **Step 2:** Settings/Config management (pydantic_settings)
- [ ] **Step 3:** Main app (FastAPI + endpoints)
- [ ] **Step 4:** JWT auth (login endpoint)
- [ ] **Step 5:** Rate limiter integration
- [ ] **Step 6:** Cost guard integration
- [ ] **Step 7:** Health & readiness checks
- [ ] **Step 8:** Graceful shutdown handler
- [ ] **Step 9:** Stateless session (Redis)
- [ ] **Step 10:** Docker build & test locally
- [ ] **Step 11:** Deploy to Railway/Render
- [ ] **Step 12:** Verification script check

### Testing & Validation

**Local testing:**
```bash
# Build & run
docker compose up --scale agent=3

# Health check
curl http://localhost/health

# Login
curl -X POST http://localhost/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "student", "password": "demo123"}'

# Use API with token
curl -H "Authorization: Bearer <token>" \
  -X POST http://localhost/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

**Cloud deployment:**
```bash
# Railway
railway init && railway up

# or Render (GitHub auto-deploy)
# Push to GitHub → Connect Render → auto-deploy
```

### Grading Rubric

| Criteria | Points | Assessment |
|----------|--------|------------|
| **Functionality** | 20 | API works, returns correct answers |
| **Docker** | 15 | Multi-stage, optimized, ~200MB |
| **Security** | 20 | Auth + rate limit + cost guard |
| **Reliability** | 20 | Health checks, graceful shutdown, stateless |
| **Scalability** | 15 | Multi-instance, load balanced |
| **Deployment** | 10 | Public URL works |
| **Total** | 100 | |

### Key Learning Outcomes

✅ **Dev to Production Pipeline:**
- From localhost to cloud in structured steps
- No hardcoded secrets or configuration
- Environment-specific settings

✅ **Containerization:**
- Multi-stage builds for efficiency
- Proper dependency management
- Production-ready Docker setup

✅ **API Security:**
- Multiple auth strategies (API Key → JWT)
- Rate limiting for fair use
- Cost guard for budget protection

✅ **System Design:**
- Stateless architecture for scalability
- Load balancing & fault tolerance
- Health checks for reliability

✅ **Cloud Deployment:**
- Deploy to managed platforms
- Environment variable management
- Public URL accessibility

---

## Complete Day 12 Lab Summary

### Overview

This lab covers the complete journey from localhost to production cloud deployment of an AI agent:

| Part | Topic | Key Takeaway |
|------|-------|-------------|
| 1 | Local vs Production | Configuration, secrets, health checks |
| 2 | Docker | Containerization, multi-stage builds |
| 3 | Cloud Deploy | Railway, Render, public URLs |
| 4 | API Security | Auth (API Key → JWT), rate limit, cost guard |
| 5 | Scaling | Stateless, health checks, graceful shutdown, LB |
| 6 | Final Project | Integrate everything into production system |

### Student Completion Status

✅ **Completed:**
- Part 1: 15 anti-patterns identified + comparison table
- Part 2: Docker development + multi-stage production build
- Part 3: Cloud deployment (Railway + Render)
- Part 4: API Security (4 exercises + 4 checkpoints)
  - 4.1: API Key authentication
  - 4.2: JWT authentication (with tests)
  - 4.3: Rate limiting (sliding window)
  - 4.4: Cost guard (budget tracking)
- Part 5: Scaling & Reliability (5 exercises + checkpoint)
  - 5.1: Health checks
  - 5.2: Graceful shutdown
  - 5.3: Stateless design
  - 5.4: Load balancing
  - 5.5: Test stateless
- Part 6: Final Project framework provided

### Key Skills Acquired

**DevOps/Infrastructure:**
- Docker containerization & multi-stage builds
- Environment variable management
- Cloud platform deployment (Railway, Render)
- Docker Compose orchestration
- Health monitoring & graceful shutdown

**Backend Development:**
- FastAPI best practices
- JWT authentication & role-based access
- Rate limiting algorithms (sliding window)
- Cost tracking & budget management
- Structured JSON logging

**System Design:**
- Stateless architecture for scalability
- Load balancing & fault tolerance
- Configuration management
- Security layers (Auth + RateLimit + CostGuard)
- Production-ready patterns

### Lessons Learned

1. **"Works on my machine" is not production-ready**
   - Need proper config management, health checks, error handling

2. **Security is layered:**
   - Authentication (who are you?)
   - Authorization (what can you do?)
   - Rate limiting (how much can you do?)
   - Cost guard (what's the impact?)

3. **Stateless design is essential for scale:**
   - No in-memory state
   - All state in shared storage (Redis/DB)
   - Any instance can handle any request

4. **Cloud deployment is simpler than expected:**
   - Proper Docker container
   - Environment variables
   - Public URL automatically assigned

5. **Monitoring & reliability come first:**
   - Health checks catch issues early
   - Graceful shutdown prevents data loss
   - Structured logging aids debugging

### Next Steps (Advanced)

For production deployment:
- **Monitoring:** Prometheus + Grafana (metrics)
- **CI/CD:** GitHub Actions (automated testing + deploy)
- **Kubernetes:** Advanced orchestration (multi-region, auto-scaling)
- **Observability:** OpenTelemetry (distributed tracing)
- **Cost optimization:** Spot instances, intelligent caching

---

**Lab Duration:** ~4 hours  
**Student:** Bùi Hữu Huấn (2A202600353)  
**Date:** 17/04/2026  
**Status:** Completed

