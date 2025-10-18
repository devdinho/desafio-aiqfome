import requests
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from aiqfome.settings.env import CACHE_TIMEOUT, FAKESTORE_BASE_URL


class FakeStoreProxyViewSet(viewsets.ViewSet):
    """
    Proxy interno para a FakeStore API com cache local.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["FakeStore Proxy"],
        operation_summary="List all products",
        operation_description="Retrieve a list of all products from the FakeStore API.",
    )
    def list(self, request):
        cache_key = "fakestore:all_products"
        data = cache.get(cache_key)

        if not data:
            response = requests.get(FAKESTORE_BASE_URL)
            if response.status_code != 200:
                return Response(
                    {"error": "Erro ao acessar API externa."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            data = response.json()
            cache.set(cache_key, data, CACHE_TIMEOUT)

        return Response(data)

    @swagger_auto_schema(
        tags=["FakeStore Proxy"],
        operation_summary="Retrieve a product by ID",
        operation_description="Retrieve detailed information about a specific product.",
    )
    def retrieve(self, request, pk=None):
        cache_key = f"fakestore:product:{pk}"
        data = cache.get(cache_key)

        if not data:
            response = requests.get(f"{FAKESTORE_BASE_URL}/{pk}")
            if not response.content:
                raise NotFound(detail="Produto não encontrado.")
            elif response.status_code != 200:
                return Response(
                    {"error": "Erro ao acessar API externa."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            data = response.json()
            cache.set(cache_key, data, CACHE_TIMEOUT)
        else:
            print(f"Produto {pk} encontrado no cache.")

        return Response(data)
