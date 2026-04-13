import random

from app.db.models.payment_intent import PaymentIntent
from app.schemas.webhook import WebhookEventPayload, WebhookPaymentData

def simulate_payment_result() -> str:
    """
    Simulate the outcome of payment processing.

    For this MVP:
    - Most payments succeed
    - Some payments fail

    Returns:
        "succeeded" or "failed"
    """
    return "succeeded" if random.random() < 0.8 else "failed"

def build_webhook_payload(payment_intent: PaymentIntent, event_id: int):
    '''
    Build the webhook payload for a payment outcome event.

    Returns a plain dict so it can be easily serialized and stored in the DB
    or sent as JSON to a merchant webhook endpoint.
    '''

    status_value = getattr(payment_intent.status, "value", payment_intent.status)
    event_type = (
        "payment.succeeded"
        if status_value == "succeeded"
        else "payment.failed"
    )

    payload = WebhookEventPayload(
        id=event_id,
        type=event_type,
        data=WebhookPaymentData(
            payment_intent_id=payment_intent.id,
            amount=payment_intent.amount,
            currency=payment_intent.currency,
            status=status_value,
        ),
    )

    return payload.model_dump()
