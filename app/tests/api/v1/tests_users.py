from fastapi.testclient import TestClient

from models.user import FirebaseUser


def test_users_get_me(
    client: TestClient, generate_token: tuple[str, FirebaseUser]
) -> None:
    token, firebase_user = generate_token
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == firebase_user.model_dump(mode="json")


def test_users_get_me_invalid_token(client: TestClient) -> None:
    response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer token"})

    assert response.status_code == 401
    assert response.json() == {
        "detail": {"code": "INVALID_TOKEN", "message": "Invalid token"}
    }
