from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 60, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.storage = {}

    async def dispatch(self, request: Request, call_next):
        key = request.client.host if request.client else 'anon'
        now = int(time.time())
        window = now - (now % self.period)
        data = self.storage.get(key, {})
        if data.get('window') != window:
            data = {'window': window, 'count': 0}
        data['count'] += 1
        self.storage[key] = data
        if data['count'] > self.calls:
            return JSONResponse({'detail':'rate limit exceeded'}, status_code=429)
        return await call_next(request)
