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


def test_cancel_payment_intent_from_requires_payment_method():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    payment_intent = create_payment_intent(api_key=api_key)
    payment_intent_id = payment_intent["id"]

    cancel_response = client.post(
        f"/payment_intents/{payment_intent_id}/cancel",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert cancel_response.status_code == 200
    cancel_data = cancel_response.json()
    assert cancel_data["id"] == payment_intent_id
    assert cancel_data["status"] == "canceled"


def test_cancel_payment_intent_twice_returns_409():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    payment_intent = create_payment_intent(api_key=api_key)
    payment_intent_id = payment_intent["id"]

    first_cancel = client.post(
        f"/payment_intents/{payment_intent_id}/cancel",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert first_cancel.status_code == 200

    second_cancel = client.post(
        f"/payment_intents/{payment_intent_id}/cancel",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert second_cancel.status_code == 409
    assert second_cancel.json()["detail"] == "Payment intent cannot be canceled in its current state."


def test_cancel_payment_intent_idempotent_same_key_replays_response():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    payment_intent = create_payment_intent(api_key=api_key)
    payment_intent_id = payment_intent["id"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Idempotency-Key": "cancel-pi-123",
    }

    first_cancel = client.post(f"/payment_intents/{payment_intent_id}/cancel", headers=headers)
    assert first_cancel.status_code == 200

    second_cancel = client.post(f"/payment_intents/{payment_intent_id}/cancel", headers=headers)
    assert second_cancel.status_code == 200

    assert first_cancel.json() == second_cancel.json()


def test_list_payment_intents_filters_status_canceled():
    merchant_data = create_test_merchant()
    api_key = merchant_data["api_key"]

    to_cancel = create_payment_intent(api_key=api_key)
    keep_open = create_payment_intent(api_key=api_key)

    cancel_response = client.post(
        f"/payment_intents/{to_cancel['id']}/cancel",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert cancel_response.status_code == 200

    list_response = client.get(
        "/payment_intents/?status=canceled",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert list_response.status_code == 200
    data = list_response.json()
    ids = [item["id"] for item in data]

    assert to_cancel["id"] in ids
    assert keep_open["id"] not in ids
