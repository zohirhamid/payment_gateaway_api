from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_test_merchant():
    response = client.post("/merchants/")
    assert response.status_code == 200
    return response.json()


def create_payment_intent(api_key: str, amount: int = 1000, currency: str = "gbp"):
    response = client.post(
        "/payment_intents/",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"amount": amount, "currency": currency},
    )
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

