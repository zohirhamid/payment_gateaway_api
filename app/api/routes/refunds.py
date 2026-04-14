from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_merchant, get_db
from app.db.models.merchant import Merchant
from app.schemas.refund import RefundListResponse, RefundResponse
from app.services.refund_service import (
    get_refund as get_refund_service,
    list_refunds_for_charge as list_refunds_for_charge_service,
)

router = APIRouter(prefix="/refunds", tags=["refunds"])


@router.get("/{refund_id}", response_model=RefundResponse)
def get_refund(
    refund_id: int,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant),
):
    refund = get_refund_service(
        db=db,
        merchant_id=current_merchant.id,
        refund_id=refund_id,
    )
    return refund


@router.get("/", response_model=RefundListResponse)
def list_refunds_for_charge(
    charge_id: int = Query(...),
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant),
):
    refunds = list_refunds_for_charge_service(
        db=db,
        merchant_id=current_merchant.id,
        charge_id=charge_id,
    )
    return RefundListResponse(refunds=[RefundResponse.model_validate(r) for r in refunds])
