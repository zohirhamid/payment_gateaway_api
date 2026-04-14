from enum import Enum


class PaymentIntentStatus(str, Enum):
    '''
    later we will add:
        requires_action
        refunded
        requires_capture
        partially_refunded
    '''
    REQUIRES_PAYMENT_METHOD = "requires_payment_method"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    PROCESSING = "processing"
    REQUIRES_CAPTURE = "requires_capture"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class ChargeStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"

class RefundStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class RefundReason(str, Enum):
    CUSTOMER_REQUEST = "customer_request"
    DUPLICATE = "duplicate"
    FRAUD = "fraud"
    PRODUCT_NOT_RECEIVED = "product_not_received"
    OTHER = "other"