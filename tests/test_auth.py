import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAuthentication:
    def test_register_user(self, client):
        url = reverse("user-register")
        response = client.post(
            url,
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "securepass123",
            },
            format="json",
        )

        assert response.status_code == 201

    def test_obtain_jwt_token(self, client, user):
        url = reverse("token_obtain_pair")
        response = client.post(
            url,
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_profile_requires_auth(self, client):
        url = reverse("user-profile")
        response = client.get(url)

        assert response.status_code == 401

    def test_profile_authenticated(self, auth_client, user):
        url = reverse("user-profile")
        response = auth_client.get(url)

        assert response.status_code == 200
        assert response.data["username"] == user.username
