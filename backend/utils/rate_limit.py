import time
import redis
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status

redis_client = redis.Redis(
    host = getattr(settings, "REDIS_HOST", "localhost"),
    port = getattr(settings, "REDIS_PORT", 6379),
    db = getattr(settings, "REDIS_DB", 0),
    decode_responses = True,
)


def rate_limit(limit: int, window: int, key_func: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            # Detect class based views or function based views
            # FBV: args = (request, ...)
            # CBV: args = (self, request, ...)
            from django.http import HttpRequest
            if args and isinstance(args[0], HttpRequest):
                request = args[0] # FBV
            elif len(args) >= 2 and isinstance(args[1], HttpRequest):
                request = args[1] # CBV
            else:
                # DRF wraps the request; fall back to first argument
                request = args[1] if len(args) >= 2 else args[0]

            # Building redis key
            # identifier = key_func(request) if key_func else request.META.get("REMOTE_ADDR", "anonymous")
            identifier = key_func if key_func else None
            current_window = int(time.time() // window)
            redis_key = f"rate_limit:{view_func.__name__}:{identifier}:{current_window}"

            # Increment counter
            counter = redis_client.incr(redis_key)
            if counter == 1:
                redis_client.expire(redis_key, window)

            # BLock if over limit
            if counter > limit:
                ttl = redis_client.ttl(redis_key)
                return JsonResponse(
                    {
                        "message": "Global Rate limit exceeded",
                        "retry_after": max(ttl, 0),
                    },
                    status = status.HTTP_429_TOO_MANY_REQUESTS,
                    headers = {
                        "Retry-After": str(max(ttl, 0)),
                        "X-RateLimit-Limit": str(limit),
                        "X-Ratelimit-Remaining": "0",
                    },
                )
            
            # Allow request
            remaining = max(limit - counter, 0)
            response = view_func(*args, **kwargs)
            response["X-RateLimit-Limit"] = str(limit)
            response["X-Ratelimit-Remaining"] = str(remaining)
            return response

        return _wrapped_view
    return decorator
















# # utils/rate_limit.py
# import time
# from functools import wraps
# import redis
# from django.http import JsonResponse

# redis_client = redis.Redis.from_url("redis://redis:6379/1", decode_responses=True)


# def rate_limit(limit: int, window: int, key_func=None):
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(*args, **kwargs):
#             # ── Detect CBV vs FBV ─────────────────────────────────────────
#             # FBV:  args = (request, ...)
#             # CBV:  args = (self, request, ...)
#             from django.http import HttpRequest
#             if args and isinstance(args[0], HttpRequest):
#                 request = args[0]           # FBV
#             elif len(args) >= 2 and isinstance(args[1], HttpRequest):
#                 request = args[1]           # CBV
#             else:
#                 # DRF wraps the request; fall back to first arg
#                 request = args[1] if len(args) >= 2 else args[0]

#             # ── Build Redis key ───────────────────────────────────────────
#             identifier = key_func(request) if key_func else request.META.get("REMOTE_ADDR", "anonymous")
#             current_window = int(time.time() // window)
#             redis_key = f"rate_limit:{view_func.__name__}:{identifier}:{current_window}"

#             # ── Increment counter ─────────────────────────────────────────
#             count = redis_client.incr(redis_key)
#             if count == 1:
#                 redis_client.expire(redis_key, window)

#             # ── Block if over limit ───────────────────────────────────────
#             if count > limit:
#                 ttl = redis_client.ttl(redis_key)
#                 return JsonResponse(
#                     {
#                         "detail": "Rate limit exceeded",
#                         "retry_after": max(ttl, 0),
#                     },
#                     status=429,
#                     headers={
#                         "Retry-After": str(max(ttl, 0)),
#                         "X-RateLimit-Limit": str(limit),
#                         "X-RateLimit-Remaining": "0",
#                     },
#                 )

#             # ── Allow request ─────────────────────────────────────────────
#             remaining = max(limit - count, 0)
#             response = view_func(*args, **kwargs)
#             response["X-RateLimit-Limit"] = str(limit)
#             response["X-RateLimit-Remaining"] = str(remaining)
#             return response

#         return _wrapped_view
#     return decorator