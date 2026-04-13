'''
How to create a charge attempt
How to mark it succeeded or failed
later, how to talk to processor integrations
'''

from sqlalchemy.orm import Session

from app.db.models.charge import Charge
from app.db.models.payment_intent import PaymentIntent
from app.services.payment_service import simulate_payment_result


def create_and_process_charge(
    *,
    db: Session,
    payment_intent: PaymentIntent,
    merchant_id: int,
) -> tuple[Charge, str | None]:
    """
    Create a charge attempt, simulate the processor result, and persist the charge outcome.

    The Charge service owns the attempt and charge result. It does not decide
    how the related PaymentIntent should transition.
    """
    charge = Charge(
        payment_intent_id=payment_intent.id,
        merchant_id=merchant_id,
        amount=payment_intent.amount,
        currency=payment_intent.currency,
        status="pending",
    )
    db.add(charge)
    db.commit()
    db.refresh(charge)

    result = simulate_payment_result()
    failure_reason = None

    if result == "succeeded":
        charge.status = "succeeded"
    else:
        charge.status = "failed"
        failure_reason = "Payment was declined"
        charge.failure_reason = failure_reason

    db.add(charge)
    db.commit()
    db.refresh(charge)

    return charge, failure_reason
