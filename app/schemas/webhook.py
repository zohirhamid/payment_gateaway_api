from datetime import datetime
from typing import Any

from pydantic import BaseModel


class WebhookPaymentData(BaseModel):
    payment_intent_id: int
    amount: int
    currency: str
    status: str


class WebhookEventPayload(BaseModel):
    id: int
    type: str
    data: WebhookPaymentData


class WebhookEventResponse(BaseModel):
    id: int
    merchant_id: int
    payment_intent_id: int
    event_type: str
    payload: dict[str, Any]
    delivery_status: str
    retry_count: int
    last_attempt_at: datetime | None
    last_error: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class WebhookRetryResponse(BaseModel):
    id: int
    delivery_status: str
    retry_count: int
    message: str

class BulkWebhookRetryResponse(BaseModel):
    scheduled_count: int
    event_ids: list[int]
    message: str