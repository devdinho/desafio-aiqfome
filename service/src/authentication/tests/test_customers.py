import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from authentication.models import Customer


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


@pytest.mark.django_db
def test_create_user_with_existing_email_fails():
    User = get_user_model()
    existing_user = User.objects.create_user(
        username="existing_user", email="existing_user@email.com", password="senha123"
    )

    client = APIClient()
    payload = {
        "first_name": "Usuário",
        "last_name": "Faminto",
        "username": "usuario_faminto",
        "password": "SenhaForte123!",
        "email": existing_user.email,
    }

    response = client.post("/api/register/", payload, format="json")
    assert response.status_code == 400, response.content

    data = response.json()
    assert "email" in data
    assert data["email"] == ["Customer com este E-mail já existe."]


@pytest.mark.django_db
def test_create_user_without_email_fails():
    client = APIClient()
    payload = {
        "first_name": "Usuário",
        "last_name": "Faminto",
        "username": "usuario_faminto",
        "password": "SenhaForte123!",
        # "email" is intentionally omitted
    }

    response = client.post("/api/register/", payload, format="json")
    assert response.status_code == 400, response.content

    data = response.json()
    assert "email" in data
    assert data["email"] == ["Este campo é obrigatório."]


@pytest.mark.django_db
def test_create_user_without_firstname_fails():
    client = APIClient()
    payload = {
        # "first_name" is intentionally omitted
        "last_name": "Faminto",
        "username": "usuario_faminto",
        "password": "SenhaForte123!",
        "email": "usuario.faminto@example.com",
    }

    response = client.post("/api/register/", payload, format="json")
    assert response.status_code == 400, response.content
    data = "".join(response.json())
    assert "first_name" in data
    assert 'null value in column "first_name"' in data


@pytest.mark.django_db
def test_create_user_without_lastname_fails():
    client = APIClient()
    payload = {
        "first_name": "Faminto",
        # "last_name" is intentionally omitted
        "username": "usuario_faminto",
        "password": "SenhaForte123!",
        "email": "usuario.faminto@example.com",
    }

    response = client.post("/api/register/", payload, format="json")
    assert response.status_code == 400, response.content
    data = "".join(response.json())
    assert "last_name" in data
    assert 'null value in column "last_name"' in data


@pytest.mark.django_db
def test_create_user_without_username_fails():
    client = APIClient()
    payload = {
        "first_name": "Usuário",
        "last_name": "Faminto",
        # "username" is intentionally omitted
        "password": "SenhaForte123!",
        "email": "usuario.faminto@example.com",
    }

    response = client.post("/api/register/", payload, format="json")
    assert response.status_code == 400, response.content
    data = response.json()
    assert "username" in data
    assert "Este campo é obrigatório." in data["username"]


@pytest.mark.django_db
def test_create_user_without_password_fails():
    client = APIClient()
    payload = {
        "first_name": "Usuário",
        "last_name": "Faminto",
        "username": "usuario_faminto",
        # "password" is intentionally omitted
        "email": "usuario.faminto@example.com",
    }

    response = client.post("/api/register/", payload, format="json")
    assert response.status_code == 400, response.content
    data = response.json()
    assert "password" in data
    assert "Este campo é obrigatório." in data["password"]


@pytest.mark.django_db
def test_edit_user_via_endpoint():
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

    data_register = response.json()
    user = Customer.objects.get(id=data_register["id"])

    login = client.post(
        "/api/login/",
        {"username": "usuario_faminto", "password": "SenhaForte123!"},
        format="json",
    )

    assert login.status_code == 200, login.content

    token = login.json().get("access")

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "first_name": "UsuárioEditado",
        "last_name": "FamintoEditado",
        "username": "usuario_faminto_editado",
        "email": "usuario.faminto.editado@example.com",
    }

    response = client.put(f"/api/customer/{user.id}", payload, format="json")
    assert response.status_code == 200, response.content
    data = response.json()
    assert data.get("first_name") == payload["first_name"]
    assert data.get("last_name") == payload["last_name"]
    assert data.get("username") == payload["username"]
    assert data.get("email") == payload["email"]
