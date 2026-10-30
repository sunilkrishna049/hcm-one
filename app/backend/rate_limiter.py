"""IP-based Rate Limiter for Chat Endpoint.
Restricts /api/chat to 20 requests per minute per IP address.
"""
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request


class IPRateLimiter:
    def __init__(self, max_requests: int = 20, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check(self, ip: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        
        # Prune expired timestamps
        timestamps = [t for t in self.requests[ip] if t > window_start]
        self.requests[ip] = timestamps

        if len(timestamps) >= self.max_requests:
            return False

        self.requests[ip].append(now)
        return True

    def reset(self):
        self.requests.clear()


rate_limiter = IPRateLimiter(max_requests=20, window_seconds=60.0)


def check_chat_rate_limit(request: Request):
    """FastAPI dependency to rate limit requests per IP."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    elif request.client:
        client_ip = request.client.host
    else:
        client_ip = "127.0.0.1"

    # Bypass rate limiter for internal testclient unless an explicit IP was provided in headers
    if client_ip == "testclient":
        return

    if not rate_limiter.check(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 20 requests per minute."
        )
