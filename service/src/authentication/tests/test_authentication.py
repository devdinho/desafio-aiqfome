import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


def _make_customer(
    first_name=True,
    last_name=True,
    username=True,
    password=True,
    email=True,
    is_superuser=False,
):
    payload = {}
    if first_name:
        payload["first_name"] = "Usuário"
    if last_name:
        payload["last_name"] = "Faminto"
    if username:
        payload["username"] = "usuario_faminto"
    if password:
        payload["password"] = "SenhaForte123!"
    if email:
        payload["email"] = "usuario.faminto@example.com"
    if is_superuser:
        payload["is_superuser"] = True

    client = APIClient()
    response = client.post("/api/register/", payload, format="json")

    return payload, response


def _make_login():
    client = APIClient()

    payload, response = _make_customer()

    assert response.status_code == 201, response.content

    response = client.post(
        "/api/login/",
        {"username": payload["username"], "password": payload["password"]},
        format="json",
    )
    return response


def _make_retrieve_customer():
    client = APIClient()
    response = _make_login()
    access_token = response.json().get("access")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = client.get(f"/api/customers", format="json")
    return access_token, response


@pytest.mark.django_db
def test_register_user():
    payload, response = _make_customer()

    assert response.status_code == 201, response.content

    data = response.json()
    assert "id" in data
    assert data.get("email") == payload["email"]

    User = get_user_model()
    assert User.objects.filter(email=payload["email"]).exists()


@pytest.mark.django_db
def test_login():
    login = _make_login()

    assert login.status_code == 200, login.content

    data = login.json()

    assert "access" in data
    assert "refresh" in data


@pytest.mark.django_db
def test_refresh_token():
    login = _make_login()

    assert login.status_code == 200, login.content

    data = login.json()
    refresh_token = data.get("refresh")

    client = APIClient()
    response = client.post(
        "/api/login/refresh/",
        {"refresh": refresh_token},
        format="json",
    )

    assert response.status_code == 200, response.content

    data = response.json()
    assert "access" in data


@pytest.mark.django_db
def test_verify_token():
    login = _make_login()

    assert login.status_code == 200, login.content

    data = login.json()
    access_token = data.get("access")
    refresh_token = data.get("refresh")

    client = APIClient()
    response = client.post(
        "/api/login/verify/",
        {"token": access_token},
        format="json",
    )

    assert response.status_code == 200, response.content

    response = client.post(
        "/api/login/verify/",
        {"token": refresh_token},
        format="json",
    )
    assert response.status_code == 200, response.content
