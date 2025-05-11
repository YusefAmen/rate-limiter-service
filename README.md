# rate-limiter-service

A FastAPI microservice and Python module that provides per-IP rate limiting using Redis. Usable as a standalone HTTP service (sidecar) or as a Python import in your own FastAPI/Python apps.

## Features

- **Endpoint:** `GET /limited`
  - Simulates a protected API route.
  - Limits requests to **5 per minute per IP** (configurable).
  - Returns `429 Too Many Requests` if the limit is exceeded.
- **Python Module:**
  - Import and use the `RateLimiter` class in your own FastAPI or Python code.
- **Implementation:**
  - Uses Redis to store request counts and timestamps.
  - Key format: `rate:<ip>`.
  - Resets count every minute using Redis TTL.

## Project Structure

```
.
├── main.py           # FastAPI app entrypoint (sidecar HTTP API)
├── rate_limiter.py   # Reusable rate limiting logic (importable module)
├── tests/            # pytest tests for rate limit scenarios
├── Dockerfile        # Containerize the app
├── docker-compose.yml# Redis + app for local testing
├── requirements.txt  # Python dependencies
└── .env.example      # Example environment variables
```

## Usage

### 1. As a Standalone HTTP Service (Sidecar/Proxy)

Run locally with Docker Compose:
```sh
docker compose up --build
```
- The FastAPI app will be available at [http://localhost:8000/limited](http://localhost:8000/limited)
- Redis will be available internally at `redis:6379`

#### **Kubernetes Sidecar Example**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-with-rate-limiter
spec:
  containers:
    - name: my-app
      image: my-app:latest
    - name: rate-limiter
      image: your-dockerhub/rate-limiter-service:latest
      env:
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: RATE_LIMIT
          value: "5"
        - name: RATE_WINDOW
          value: "60"
      ports:
        - containerPort: 8000
```

**How to use:**
- Your app makes HTTP requests to `http://localhost:8000/limited` to check if the current request is allowed.
- If the response is 200, proceed; if 429, reject or throttle.

#### **Test the Rate Limit with cURL**
```sh
# Make 5 allowed requests
for i in {1..5}; do curl -i http://localhost:8000/limited; done
# 6th request should return 429
curl -i http://localhost:8000/limited
```

### 2. As a Python Module

Install dependencies:
```sh
pip install -r requirements.txt
```

**Example usage in your own FastAPI app:**
```python
from rate_limiter import RateLimiter

rate_limiter = RateLimiter(redis_url="redis://localhost:6379", rate_limit=5, rate_window=60)

async def my_endpoint():
    allowed = await rate_limiter.is_allowed("rate:some-unique-key")
    if not allowed:
        # handle rate limit exceeded
        ...
```

**You can also use the `get_client_ip(request)` helper for extracting IPs from FastAPI requests.**

## Testing

Run tests with pytest (requires a running Redis):
```sh
docker compose run --rm app pytest
```

## Notes
- The rate limit is enforced per key (e.g., per IP or user).
- The limit and window can be configured via environment variables (see `.env.example`).
- For production, ensure Redis is secured and persistent.

## SRE/DevOps Tips
- Use `docker compose logs app` and `docker compose logs redis` for debugging.
- Monitor Redis memory usage if running at scale.
- You can adjust the rate limit by changing environment variables and restarting the service. 