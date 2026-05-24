"""Authentication API tests."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_me_with_invalid_token_returns_401() -> None:
    """Reject invalid bearer tokens on protected routes."""

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token."
