def test_signup_login_and_create_model(client):
    signup = client.post(
        "/api/v1/auth/signup",
        json={"email": "owner@example.com", "password": "Password123!", "full_name": "Owner"},
    )
    assert signup.status_code == 201, signup.text
    token = signup.json()["access_token"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert login.status_code == 200, login.text

    headers = {"Authorization": f"Bearer {token}"}
    create_model = client.post(
        "/api/v1/models",
        headers=headers,
        json={
            "name": "Customer Support Bot",
            "description": "Answers common support questions.",
            "category": "text_to_text",
            "visibility": "private",
            "improve_from_feedback": True,
        },
    )
    assert create_model.status_code == 201, create_model.text
    body = create_model.json()
    assert body["name"] == "Customer Support Bot"
    assert body["slug"] == "customer-support-bot"
    assert body["improve_from_feedback"] is True

    models = client.get("/api/v1/models", headers=headers)
    assert models.status_code == 200
    assert len(models.json()) == 1


def test_models_are_owner_scoped(client, auth_headers):
    first = client.post(
        "/api/v1/models",
        headers=auth_headers,
        json={"name": "Private Model", "category": "text_to_text"},
    )
    assert first.status_code == 201
    model_id = first.json()["id"]

    second_signup = client.post(
        "/api/v1/auth/signup",
        json={"email": "other@example.com", "password": "Password123!", "full_name": "Other"},
    )
    second_token = second_signup.json()["access_token"]
    second_headers = {"Authorization": f"Bearer {second_token}"}

    blocked = client.get(f"/api/v1/models/{model_id}", headers=second_headers)
    assert blocked.status_code == 404
