import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_create_user_via_register_endpoint():
    client = APIClient()
    payload = {
        "first_name": "Usuário",
        "last_name": "Faminto",
        "username": "usuario_faminto",
        "password": "SenhaForte123!",
        "email": "usuario.faminto@example.com",
    }

    response = client.post("/api/register/", payload, format="json")
    assert response.status_code == 201, response.content

    data = response.json()
    assert "id" in data
    assert data.get("email") == payload["email"]

    User = get_user_model()
    assert User.objects.filter(email=payload["email"]).exists()
