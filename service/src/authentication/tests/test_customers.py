import pytest
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient

from authentication.tests.test_authentication import (
    _make_customer,
    _make_retrieve_customer,
)


@pytest.mark.django_db
def test_create_user_with_existing_email_fails():
    _, first_response = _make_customer()
    assert first_response.status_code == 201, first_response.content

    _, last_response = _make_customer()
    assert last_response.status_code == 400, last_response.content

    data = last_response.json()
    assert "email" in data
    assert data["email"] == ["Customer com este E-mail já existe."]


@pytest.mark.django_db
def test_create_user_without_email_fails():
    _, response = _make_customer(email=False)

    assert response.status_code == 400, response.content

    data = response.json()
    assert "email" in data
    assert data["email"] == ["Este campo é obrigatório."]


@pytest.mark.django_db
def test_create_user_without_firstname_fails():
    _, response = _make_customer(first_name=False)
    assert response.status_code == 400, response.content
    data = "".join(response.json())
    assert "first_name" in data
    assert 'null value in column "first_name"' in data


@pytest.mark.django_db
def test_create_user_without_lastname_fails():
    _, response = _make_customer(last_name=False)

    assert response.status_code == 400, response.content
    data = "".join(response.json())
    assert "last_name" in data
    assert 'null value in column "last_name"' in data


@pytest.mark.django_db
def test_create_user_without_username_fails():
    _, response = _make_customer(username=False)

    assert response.status_code == 400, response.content
    data = response.json()
    assert "username" in data
    assert "Este campo é obrigatório." in data["username"]


@pytest.mark.django_db
def test_create_user_without_password_fails():
    _, response = _make_customer(password=False)
    assert response.status_code == 400, response.content
    data = response.json()
    assert "password" in data
    assert "Este campo é obrigatório." in data["password"]


@pytest.mark.django_db
def test_edit_user_via_endpoint():
    access_token, response = _make_retrieve_customer()

    assert response.status_code == 200, response.content

    data = response.json()
    user_id = data.get("id")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    """ Dados do usuário antigo:
        {
            "id": 1,
            "first_name": "Usuário",
            "last_name": "Faminto",
            "username": "usuario_faminto",
            "email": "usuario.faminto@example.com"
        }
    """

    payload = {
        "first_name": "UsuárioEditado",
        "last_name": "FamintoEditado",
        "username": "usuario_faminto_editado",
        "email": "usuario.faminto.editado@example.com",
    }

    response = client.put(f"/api/customers/{user_id}", payload, format="json")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data.get("first_name") == payload["first_name"]
    assert data.get("last_name") == payload["last_name"]
    assert data.get("username") == payload["username"]
    assert data.get("email") == payload["email"]


@pytest.mark.django_db
def test_edit_user_partial_update():
    access_token, response = _make_retrieve_customer()

    assert response.status_code == 200, response.content

    data = response.json()
    user_id = data.get("id")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    payload = {
        "first_name": "UsuárioEditado",
        "last_name": "FamintoEditado",
    }

    response = client.patch(f"/api/customers/{user_id}", payload, format="json")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data.get("first_name") == payload["first_name"]
    assert data.get("last_name") == payload["last_name"]


@pytest.mark.django_db
def test_retrieve_customer_by_id():
    access_token, response = _make_retrieve_customer()

    data = response.json()
    user_id = data.get("id")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = client.get(f"/api/customers/{user_id}", format="json")

    assert response.status_code == 200, response.content

    data_by_id = response.json()

    assert data_by_id.get("id") == user_id
    assert data_by_id.get("first_name") == data.get("first_name")
    assert data_by_id.get("last_name") == data.get("last_name")
    assert data_by_id.get("username") == data.get("username")
    assert data_by_id.get("email") == data.get("email")


@override_settings(SIMPLE_HISTORY_ENABLED=False)
class TestDeleteUser(TransactionTestCase):
    @pytest.mark.django_db
    def test_delete_user_via_endpoint(self):
        """
        Testa a exclusão de um usuário via endpoint.

        OBS: desabilitamos temporariamente o Simple History neste teste
        porque, durante a deleção, o histórico tenta registrar o próprio usuário
        como 'history_user'. Como isso acontece na mesma transação, o banco
        gera IntegrityError na FK. Fora dos testes (ex: Swagger), cada request
        é transacionalmente isolada, então funciona normalmente.
        """
        access_token, response = _make_retrieve_customer()
        assert response.status_code == 200, response.content

        data = response.json()
        user_id = data.get("id")

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = client.delete(f"/api/customers/{user_id}", format="json")
        assert response.status_code == 204

        payload, response = _make_customer(is_superuser=True)

        assert response.status_code == 201, response.content
        admin_login = client.post(
            "/api/login/",
            {"username": payload["username"], "password": payload["password"]},
            format="json",
        )
        assert admin_login.status_code == 200, admin_login.content
        admin_access_token = admin_login.json().get("access")
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_access_token}")

        response = client.get(f"/api/customers/{user_id}", format="json")
        data = response.json()

        assert response.status_code == 404, response.content
        assert data.get("detail") == "No Customer matches the given query."
