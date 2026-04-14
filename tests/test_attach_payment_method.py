from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.core.config import settings

# Create test database
engine = create_engine(settings.database_url)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


def create_test_merchant():
    response = client.post("/merchants/")
    print(f"Merchant creation response: {response.status_code} - {response.text}")
    assert response.status_code == 200
    return response.json()


def create_payment_intent(api_key: str, amount: int = 1000, currency: str = "GBP"):
    print(f"Creating payment intent with amount={amount}, currency={currency}")
    response = client.post(
        "/payment_intents/",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"amount": amount, "currency": currency},
    )
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    if response.status_code != 200:
        print(f"Error response: {response.json()}")
    assert response.status_code == 200
    return response.json()


def test_attach_payment_method_moves_to_requires_confirmation():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    payment_intent = create_payment_intent(api_key=api_key)
    payment_intent_id = payment_intent["id"]

    attach_response = client.post(
        f"/payment_intents/{payment_intent_id}/attach_payment_method",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"payment_method_reference": "pm_test_123"},
    )
    assert attach_response.status_code == 200
    data = attach_response.json()
    assert data["id"] == payment_intent_id
    assert data["status"] == "requires_confirmation"


def test_attach_payment_method_twice_returns_409():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    payment_intent = create_payment_intent(api_key=api_key)
    payment_intent_id = payment_intent["id"]

    first_attach = client.post(
        f"/payment_intents/{payment_intent_id}/attach_payment_method",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"payment_method_reference": "pm_test_123"},
    )
    assert first_attach.status_code == 200

    second_attach = client.post(
        f"/payment_intents/{payment_intent_id}/attach_payment_method",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"payment_method_reference": "pm_test_456"},
    )
    assert second_attach.status_code == 409
    assert second_attach.json()["detail"] == "Payment method cannot be attached in the current state."

