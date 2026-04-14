import time
from dataclasses import dataclass

from fastapi import Depends, HTTPException

from app.db.models.merchant import Merchant


@dataclass(frozen=True)
class RateLimitRule:
    scope: str
    limit: int
    window_seconds: int

@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    current_count: int
    remaining: int
    retry_after: int
    reset_after: int


def raise_rate_limit_exceeded(rule: RateLimitRule, result: RateLimitResult) -> None:
    raise HTTPException(
        status_code=429,
        detail={
            "message": "Rate limit exceeded",
            "scope": rule.scope,
            "retry_after": result.retry_after,
        },
        headers={"Retry-After": str(result.retry_after)},
    )

def get_window_start(now: int, window_seconds: int) -> int:
    return now - (now % window_seconds)

def get_window_reset(now: int, window_seconds: int) -> int:
    return get_window_start(now, window_seconds) + window_seconds - now
    
def build_rate_limit_key(scope: str, merchant_id: str, window_start):
    return f"rate_limit:{scope}:merchant:{merchant_id}:{window_start}"

def check_rate_limit(redis, now: int, rule: RateLimitRule, merchant_id: str) -> RateLimitResult:
    window_start = get_window_start(now, rule.window_seconds)
    retry_after = get_window_reset(now, rule.window_seconds)
    redis_key = build_rate_limit_key(rule.scope, merchant_id, window_start)

    current_count = redis.incr(redis_key)

    if current_count == 1:
        redis.expire(redis_key, retry_after)

    allowed = current_count <= rule.limit
    remaining = max(0, rule.limit - current_count)

    return RateLimitResult(
        allowed=allowed,
        limit=rule.limit,
        current_count=current_count,
        remaining=remaining,
        retry_after=retry_after if not allowed else 0,
        reset_after=retry_after,
    )


def enforce_rate_limit(redis, merchant_id: str, rule: RateLimitRule) -> RateLimitResult:
    now = int(time.time())
    result = check_rate_limit(redis, now, rule, merchant_id)

    if not result.allowed:
        raise_rate_limit_exceeded(rule, result)

    return result