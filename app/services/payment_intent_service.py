import json

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.enums import PaymentIntentStatus
from app.db.models.payment_intent import PaymentIntent
from app.schemas.payment_intent import PaymentIntentCreate
from app.services.charge_service import create_and_process_charge
from app.services.idempotency_service import (
    create_idempotency_record,
    get_idempotency_record,
)
from app.services.payment_service import build_webhook_payload
from app.services.payment_state_machine import apply_payment_intent_status_transition
from app.services.webhook_service import create_webhook_event
from app.utils.hashing import hash_request_payload


def create_payment_intent(
    *,
    db: Session,
    merchant_id: int,
    payload: PaymentIntentCreate,
    idempotency_key: str | None,
) -> dict:
    '''
    Output: Dict matching `PaymentIntentResponse` shape.
    '''

    endpoint = "create_payment_intent"
    request_hash = hash_request_payload(payload.model_dump())

    if idempotency_key:
        existing_record = get_idempotency_record(
            db=db,
            merchant_id=merchant_id,
            endpoint=endpoint,
            idempotency_key=idempotency_key,
        )
        if existing_record:
            if existing_record.request_hash != request_hash:
                raise HTTPException(
                    status_code=409,
                    detail="Idempotency key was already used with a different payload.",
                )
            return json.loads(existing_record.response_body)

    payment_intent = PaymentIntent(
        merchant_id=merchant_id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        status=PaymentIntentStatus.REQUIRES_PAYMENT_METHOD,
    )

    db.add(payment_intent)
    db.commit()
    db.refresh(payment_intent)

    response_payload = {
        "id": payment_intent.id,
        "merchant_id": payment_intent.merchant_id,
        "amount": payment_intent.amount,
        "currency": payment_intent.currency,
        "status": getattr(payment_intent.status, "value", payment_intent.status),
        "created_at": payment_intent.created_at.isoformat(),  # type: ignore[union-attr]
    }

    if idempotency_key:
        create_idempotency_record(
            db=db,
            merchant_id=merchant_id,
            endpoint=endpoint,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            response_status_code=200,
            response_body=json.dumps(response_payload),
        )

    return response_payload


def get_payment_intent(
    *,
    db: Session,
    merchant_id: int,
    payment_intent_id: int,
) -> PaymentIntent:
    """
    Fetch a single payment intent scoped to a merchant.

    Inputs:
        db: SQLAlchemy session.
        merchant_id: Authenticated merchant id (ownership scope).
        payment_intent_id: Payment intent id to fetch.

    Output:
        PaymentIntent model instance.
    """
    payment_intent = (
        db.query(PaymentIntent)
        .filter(
            PaymentIntent.id == payment_intent_id,
            PaymentIntent.merchant_id == merchant_id,
        )
        .first()
    )

    if payment_intent is None:
        raise HTTPException(status_code=404, detail="Payment intent not found.")

    return payment_intent


def list_payment_intents(
    *,
    db: Session,
    merchant_id: int,
    status: PaymentIntentStatus | None = None,
    currency: str | None = None,
    amount_gte: int | None = None,
    amount_lte: int | None = None,
    created_at_gte: datetime | None = None,
    created_at_lte: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[PaymentIntent]:
    """
    List payment intents scoped to a merchant.

    Inputs:
        db: SQLAlchemy session.
        merchant_id: Authenticated merchant id (ownership scope).
        status: Optional filter by PaymentIntent status.
        currency: Optional filter by 3-letter currency (case-insensitive).
        amount_gte: Optional minimum amount (inclusive).
        amount_lte: Optional maximum amount (inclusive).
        created_at_gte: Optional earliest created_at (inclusive).
        created_at_lte: Optional latest created_at (inclusive).
        limit: Max rows to return.
        offset: Rows to skip (pagination).

    Output:
        List of PaymentIntent model instances, newest-first.
    """
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    query = db.query(PaymentIntent).filter(PaymentIntent.merchant_id == merchant_id)

    if status is not None:
        query = query.filter(PaymentIntent.status == status)

    if currency:
        query = query.filter(PaymentIntent.currency == currency.upper())

    if amount_gte is not None:
        query = query.filter(PaymentIntent.amount >= amount_gte)

    if amount_lte is not None:
        query = query.filter(PaymentIntent.amount <= amount_lte)

    if created_at_gte is not None:
        query = query.filter(PaymentIntent.created_at >= created_at_gte)

    if created_at_lte is not None:
        query = query.filter(PaymentIntent.created_at <= created_at_lte)

    return (
        query.order_by(PaymentIntent.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def cancel_payment_intent(
    *,
    db: Session,
    merchant_id: int,
    payment_intent_id: int,
    idempotency_key: str | None,
) -> dict:
    """
    Cancel a payment intent (only allowed before processing).

    Output:
        Dict matching `PaymentIntentResponse` shape.
    """

    endpoint = "cancel_payment_intent"
    request_hash = hash_request_payload({"payment_intent_id": payment_intent_id})

    if idempotency_key:
        existing_record = get_idempotency_record(
            db=db,
            merchant_id=merchant_id,
            endpoint=endpoint,
            idempotency_key=idempotency_key,
        )
        if existing_record:
            if existing_record.request_hash != request_hash:
                raise HTTPException(
                    status_code=409,
                    detail="Idempotency key was already used with a different payload.",
                )
            return json.loads(existing_record.response_body)

    payment_intent = (
        db.query(PaymentIntent)
        .filter(
            PaymentIntent.id == payment_intent_id,
            PaymentIntent.merchant_id == merchant_id,
        )
        .first()
    )

    if payment_intent is None:
        raise HTTPException(status_code=404, detail="Payment intent not found.")

    if payment_intent.status not in {
        PaymentIntentStatus.REQUIRES_PAYMENT_METHOD,
        PaymentIntentStatus.REQUIRES_CONFIRMATION,
    }:
        raise HTTPException(
            status_code=409,
            detail="Payment intent cannot be canceled in its current state.",
        )

    payment_intent = apply_payment_intent_status_transition(
        db=db,
        payment_intent=payment_intent,
        new_status=PaymentIntentStatus.CANCELED,
    )

    response_payload = {
        "id": payment_intent.id,
        "merchant_id": payment_intent.merchant_id,
        "amount": payment_intent.amount,
        "currency": payment_intent.currency,
        "status": getattr(payment_intent.status, "value", payment_intent.status),
        "created_at": payment_intent.created_at.isoformat(),  # type: ignore[union-attr]
    }

    if idempotency_key:
        create_idempotency_record(
            db=db,
            merchant_id=merchant_id,
            endpoint=endpoint,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            response_status_code=200,
            response_body=json.dumps(response_payload),
        )

    return response_payload


def confirm_payment_intent(
    *,
    db: Session,
    merchant_id: int,
    payment_intent_id: int,
    idempotency_key: str | None,
) -> tuple[dict, int | None]:
    """
    Confirm a payment intent and simulate a payment attempt.

    Output:
        (confirm_response_payload, webhook_event_id)

        If an idempotency record is replayed, webhook_event_id is None to avoid
        scheduling duplicate webhook delivery.
    """

    endpoint = "confirm_payment_intent"
    request_hash = hash_request_payload({"payment_intent_id": payment_intent_id})

    if idempotency_key:
        existing_record = get_idempotency_record(
            db=db,
            merchant_id=merchant_id,
            endpoint=endpoint,
            idempotency_key=idempotency_key,
        )
        if existing_record:
            if existing_record.request_hash != request_hash:
                raise HTTPException(
                    status_code=409,
                    detail="Idempotency key was already used with a different payload.",
                )
            return json.loads(existing_record.response_body), None

    payment_intent = (
        db.query(PaymentIntent)
        .filter(
            PaymentIntent.id == payment_intent_id,
            PaymentIntent.merchant_id == merchant_id,
        )
        .first()
    )

    if payment_intent is None:
        raise HTTPException(status_code=404, detail="Payment intent not found.")

    # Only confirm once in this MVP.
    if payment_intent.status != PaymentIntentStatus.REQUIRES_PAYMENT_METHOD:
        raise HTTPException(
            status_code=409,
            detail="Payment intent has already been processed or is not confirmable.",
        )

    payment_intent = apply_payment_intent_status_transition(
        db=db,
        payment_intent=payment_intent,
        new_status=PaymentIntentStatus.REQUIRES_CONFIRMATION,
    )

    payment_intent = apply_payment_intent_status_transition(
        db=db,
        payment_intent=payment_intent,
        new_status=PaymentIntentStatus.PROCESSING,
    )

    charge, failure_reason = create_and_process_charge(
        db=db,
        payment_intent=payment_intent,
        merchant_id=merchant_id,
    )

    payment_intent = apply_payment_intent_status_transition(
        db=db,
        payment_intent=payment_intent,
        new_status=(
            PaymentIntentStatus.SUCCEEDED
            if charge.status == "succeeded"
            else PaymentIntentStatus.FAILED
        ),
        failure_reason=failure_reason,
    )

    event_type = (
        "payment.succeeded"
        if payment_intent.status == PaymentIntentStatus.SUCCEEDED
        else "payment.failed"
    )

    webhook_payload = build_webhook_payload(payment_intent=payment_intent, event_id=0)

    webhook_event = create_webhook_event(
        db=db,
        merchant_id=merchant_id,
        payment_intent_id=payment_intent.id,
        event_type=event_type,
        payload=webhook_payload,
    )

    response_payload = {
        "payment_intent_id": payment_intent.id,
        "charge_id": charge.id,
        "status": getattr(payment_intent.status, "value", payment_intent.status),
    }

    if idempotency_key:
        create_idempotency_record(
            db=db,
            merchant_id=merchant_id,
            endpoint=endpoint,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            response_status_code=200,
            response_body=json.dumps(response_payload),
        )

    return response_payload, webhook_event.id
