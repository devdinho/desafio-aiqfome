import pytest
from rest_framework.test import APIClient

from authentication.tests.test_authentication import _make_login


def _make_favorite(user_token, product_id):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")

    response = client.post(
        "/api/favorites",
        {"product_id": product_id},
        format="json",
    )

    return response


@pytest.mark.django_db
def test_add_favorite():
    login_response = _make_login()
    user_token = login_response.json().get("access")
    product_id = 1

    response = _make_favorite(user_token, product_id)

    assert response.status_code == 201, response.content


@pytest.mark.django_db
def test_add_favorite_unauthenticated():
    client = APIClient()
    product_id = 1

    response = client.post(
        "/api/favorites",
        {"product_id": product_id},
    )

    assert response.status_code == 401, response.content


@pytest.mark.django_db
def test_add_favorite_invalid_product():
    login_response = _make_login()
    user_token = login_response.json().get("access")
    invalid_product_id = 9999

    response = _make_favorite(user_token, invalid_product_id)

    assert response.status_code == 404, response.content
    assert response.json().get("detail") == "Produto não encontrado."


@pytest.mark.django_db
def test_add_favorite_duplicate():
    login_response = _make_login()
    user_token = login_response.json().get("access")
    product_id = 1

    first_response = _make_favorite(user_token, product_id)
    assert first_response.status_code == 201, first_response.content

    second_response = _make_favorite(user_token, product_id)
    assert second_response.status_code == 400, second_response.content
    assert "".join(second_response.json()) == "Produto já está nos favoritos."


@pytest.mark.django_db
def test_get_favorites():
    login_response = _make_login()
    user_token = login_response.json().get("access")

    _make_favorite(user_token, 1)
    _make_favorite(user_token, 2)
    _make_favorite(user_token, 3)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")

    response = client.get("/api/favorites")

    assert response.status_code == 200, response.content

    favorites = response.json()

    assert len(favorites) == 3
    assert favorites[0]["product_id"] == 3
    assert favorites[1]["product_id"] == 2
    assert favorites[2]["product_id"] == 1


@pytest.mark.django_db
def test_get_favorite_by_id():
    login_response = _make_login()
    user_token = login_response.json().get("access")

    favorite_response = _make_favorite(user_token, 1)
    favorite_id = favorite_response.json().get("id")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")

    response = client.get(f"/api/favorites/{favorite_id}")

    assert response.status_code == 200, response.content

    favorite = response.json()

    assert favorite["id"] == favorite_id
    assert favorite["product_id"] == 1


@pytest.mark.django_db
def test_get_favorite_by_id_not_found():
    login_response = _make_login()
    user_token = login_response.json().get("access")
    import uuid

    non_existent_favorite_id = uuid.uuid7()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")

    response = client.get(f"/api/favorites/{non_existent_favorite_id}")

    assert response.status_code == 404, response.content
    assert response.json().get("detail") == "No Favorites matches the given query."


@pytest.mark.django_db
def test_deactivate_favorite():
    login_response = _make_login()
    user_token = login_response.json().get("access")

    favorite_response = _make_favorite(user_token, 1)
    favorite_id = favorite_response.json().get("id")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")

    response = client.delete(f"/api/favorites/{favorite_id}")

    assert response.status_code == 204, response.content

    get_response = client.get(f"/api/favorites/{favorite_id}")
    assert get_response.status_code == 404, get_response.content
