from fastapi import FastAPI, Request, HTTPException
from rate_limiter import RateLimiter, get_client_ip

app = FastAPI()
rate_limiter = RateLimiter()

@app.get("/limited")
async def limited(request: Request):
    ip = get_client_ip(request)
    key = f"rate:{ip}"
    allowed = await rate_limiter.is_allowed(key)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return {"message": "Request allowed"} 