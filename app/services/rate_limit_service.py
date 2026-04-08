'''
decide whether a merchant can proceed on a given endpoint.
Answers: "Has this merchant exceeded the allowed request count for this endpoint
in the current time window?"
'''

'''
Rate Limiting Settings:
create payment intent limit = 10
create payment intent window seconds = 60
confirm payment intent limit = 5
confirm payment intent window seconds = 60
'''
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.rate_limit_log import RateLimitLog


def count_recent_requests(
    db: Session, merchant_id: int,
    endpoint: str, window_seconds: int) -> int:

    window_start = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)

    return (
        db.query(RateLimitLog)
        .filter(
            RateLimitLog.merchant_id == merchant_id,
            RateLimitLog.endpoint == endpoint,
            RateLimitLog.created_at >= window_start,
        )
        .count()
    )


def create_rate_limit_log(
    db: Session, merchant_id: int, endpoint: str) -> RateLimitLog:
    """
    Store one allowed request so it counts toward the merchant's
    current rate limit window.
    """
    log = RateLimitLog(
        merchant_id=merchant_id,
        endpoint=endpoint,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def enforce_rate_limit(
    db: Session, merchant_id: int, endpoint: str,
    max_requests: int, window_seconds: int) -> None:
    """
    Enforce a fixed-window rate limit for one merchant and one endpoint.

    If the merchant has already reached the maximum number of requests
    allowed in the current window, raise HTTP 429.

    Otherwise, record the allowed request and let processing continue.
    """
    recent_request_count = count_recent_requests(
        db=db,
        merchant_id=merchant_id,
        endpoint=endpoint,
        window_seconds=window_seconds,
    )

    if recent_request_count >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
            },
        )

    create_rate_limit_log(
        db=db,
        merchant_id=merchant_id,
        endpoint=endpoint,
    )


'''TODO:
replace this with deps later
'''