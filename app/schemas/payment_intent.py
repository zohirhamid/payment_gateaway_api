"""Pydantic schemas used by the PaymentIntent API endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PaymentIntentCreate(BaseModel):
    amount: int
    currency: str

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v, info):
        currency = info.data.get('currency', '').upper()

        # Maximum amount: 99999999 (about $1M for USD)
        if v > 99999999:
            raise ValueError('Amount exceeds maximum allowed value')
            
        
        # currency specific minimums
        min_amounts = {
            'USD': 50,  # 50 cents minimum
            'EUR': 50,  # 50 cents minimum
            'GBP': 30,  # 30 pence minimum
            'JPY': 1,   # 1 yen minimum
        }
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        supported_currencies = {'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD'}
        if v.upper() not in supported_currencies:
            raise ValueError(f'Currency {v} is not supported')
        return v.upper()



class PaymentIntentResponse(BaseModel):
    id: int
    merchant_id: int
    amount: int
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentIntentConfirmResponse(BaseModel):
    payment_intent_id: int
    charge_id: int
    status: str


class PaymentIntentAttachPaymentMethod(BaseModel):
    payment_method_reference: str = Field(..., min_length=1)
