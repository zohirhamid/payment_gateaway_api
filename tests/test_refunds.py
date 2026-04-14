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
        json={
            "amount": amount,
            "currency": currency,
        },
    )
    assert response.status_code == 200
    return response.json()


def attach_payment_method(api_key: str, payment_intent_id: int):
    response = client.post(
        f"/payment_intents/{payment_intent_id}/attach_payment_method",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"payment_method_reference": "pm_test"},
    )
    assert response.status_code == 200
    return response.json()


def confirm_payment_intent(api_key: str, payment_intent_id: int):
    response = client.post(
        f"/payment_intents/{payment_intent_id}/confirm",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200
    return response.json()


def capture_payment_intent(api_key: str, payment_intent_id: int):
    response = client.post(
        f"/payment_intents/{payment_intent_id}/capture",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200
    return response.json()


def test_create_refund_for_charge():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    payment_intent = create_payment_intent(api_key=api_key, amount=1200, currency="usd")
    payment_intent_id = payment_intent["id"]

    attach_payment_method(api_key, payment_intent_id)
    confirm_response = confirm_payment_intent(api_key, payment_intent_id)
    assert confirm_response["status"] == "requires_capture"
    charge_id = confirm_response["charge_id"]

    capture_response = capture_payment_intent(api_key, payment_intent_id)
    assert capture_response["status"] == "succeeded"

    refund_response = client.post(
        f"/charges/{charge_id}/refunds",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"reason": "customer_request"},
    )
    assert refund_response.status_code == 200

    refund_data = refund_response.json()
    assert refund_data["charge_id"] == charge_id
    assert refund_data["payment_intent_id"] == payment_intent_id
    assert refund_data["merchant_id"] == merchant_data["id"]
    assert refund_data["amount"] == 1200
    assert refund_data["currency"] == "USD"
    assert refund_data["status"] == "succeeded"
    assert refund_data["reason"] == "customer_request"


def test_refund_full_charge_twice_returns_conflict():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    payment_intent = create_payment_intent(api_key=api_key, amount=1500, currency="gbp")
    payment_intent_id = payment_intent["id"]

    attach_payment_method(api_key, payment_intent_id)
    confirm_response = confirm_payment_intent(api_key, payment_intent_id)
    charge_id = confirm_response["charge_id"]

    capture_payment_intent(api_key, payment_intent_id)

    first_refund = client.post(
        f"/charges/{charge_id}/refunds",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"reason": "duplicate"},
    )
    assert first_refund.status_code == 200

    second_refund = client.post(
        f"/charges/{charge_id}/refunds",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"reason": "duplicate"},
    )
    assert second_refund.status_code == 409
    assert second_refund.json()["detail"] == "Charge has already been fully refunded."
