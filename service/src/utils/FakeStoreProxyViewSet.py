import requests
from aiqfome.settings.env import FAKESTORE_BASE_URL, CACHE_TIMEOUT
from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class FakeStoreProxyViewSet(viewsets.ViewSet):
    """
    Proxy interno para a FakeStore API com cache local.
    """
    permission_classes = [AllowAny]

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

    def retrieve(self, request, pk=None):
        cache_key = f"fakestore:product:{pk}"
        data = cache.get(cache_key)

        if not data:
            response = requests.get(f"{FAKESTORE_BASE_URL}/{pk}")
            if response.status_code == 404:
                raise NotFound(detail="Produto não encontrado.")
            elif response.status_code != 200:
                return Response(
                    {"error": "Erro ao acessar API externa."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            data = response.json()
            cache.set(cache_key, data, CACHE_TIMEOUT)
        else:
            print(f'Produto {pk} encontrado no cache.')
        
        return Response(data)
