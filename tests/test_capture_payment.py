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


def attach_payment_method(api_key: str, payment_intent_id: int, payment_method_ref: str = "pm_test"):
    response = client.post(
        f"/payment_intents/{payment_intent_id}/attach_payment_method",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"payment_method_reference": payment_method_ref},
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


def test_capture_payment_intent():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    payment_intent = create_payment_intent(api_key=api_key)
    payment_intent_id = payment_intent["id"]

    # Attach payment method
    attach_payment_method(api_key, payment_intent_id)

    # Confirm to authorize
    confirm_data = confirm_payment_intent(api_key, payment_intent_id)
    assert confirm_data["status"] == "requires_capture"

    # Now capture
    capture_response = client.post(
        f"/payment_intents/{payment_intent_id}/capture",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert capture_response.status_code == 200

    capture_data = capture_response.json()
    assert capture_data["id"] == payment_intent_id
    assert capture_data["status"] == "succeeded"

    # Try to capture again
    second_capture_response = client.post(
        f"/payment_intents/{payment_intent_id}/capture",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert second_capture_response.status_code == 409
    assert second_capture_response.json()["detail"] == (
        "Payment intent cannot be captured in its current state."
    )