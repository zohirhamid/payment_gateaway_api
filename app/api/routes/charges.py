from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_merchant, get_db
from app.db.models.merchant import Merchant
from app.schemas.refund import RefundCreate, RefundResponse
from app.services.refund_service import process_refund

router = APIRouter(prefix="/charges", tags=["charges"])


@router.post("/{charge_id}/refunds", response_model=RefundResponse)
def create_refund_for_charge(
    charge_id: int,
    payload: RefundCreate,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant),
):
    refund = process_refund(
        db=db,
        merchant_id=current_merchant.id,
        charge_id=charge_id,
        reason=payload.reason,
    )
    return refund
