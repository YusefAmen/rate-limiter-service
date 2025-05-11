# Deprecated: Use get_client_ip from rate_limiter.py
# from fastapi import Request
# def get_client_ip(request: Request) -> str:
#     xff = request.headers.get("x-forwarded-for")
#     if xff:
#         return xff.split(",")[0].strip()
#     return request.client.host 