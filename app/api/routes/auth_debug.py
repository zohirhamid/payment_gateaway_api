from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.merchant import Merchant

from app.schemas.merchant import MerchantResponse

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "ok"
        }

@router.post("/test-merchants", response_model=MerchantResponse)
def create_test_merchant(db: Session = Depends(get_db)):
    merchant = Merchant(
        name="Test Merchant"
        )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    return merchant # return an SQLAlchemy instead of JSON

@router.get("/merchants")
def list_test_merchants(db: Session = Depends(get_db)):
    merchants = db.query(Merchant).all()

    return [
        {
            "id": merchant.id,
            "name": merchant.name,
        }
        for merchant in merchants
    ]