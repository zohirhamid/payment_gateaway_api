from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import RefundReason, RefundStatus


class RefundCreate(BaseModel):
    reason: RefundReason


class RefundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    charge_id: int
    payment_intent_id: int
    merchant_id: int
    amount: int
    currency: str
    status: RefundStatus
    reason: RefundReason
    failure_reason: str | None
    created_at: datetime
    succeeded_at: datetime | None
    failed_at: datetime | None


class RefundListResponse(BaseModel):
    refunds: list[RefundResponse]
