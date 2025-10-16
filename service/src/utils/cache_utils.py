"""Helpers para manipulação de cache compartilhados pela aplicação.

Atualmente contém utilitários para atualizar o cache de favoritos do usuário.
"""
from django.core.cache import cache

from aiqfome.settings import CACHE_TIMEOUT
from aiqfome.models import Favorites
from aiqfome.serializers import FavoritesSerializer


def update_favorites_cache_for_user(user_id):
    """Atualiza o cache de favoritos do usuário e retorna os dados serializados.

    Args:
        user_id (int): id do usuário (customer) cujo cache deve ser atualizado.

    Returns:
        list: lista serializada de favoritos ativos do usuário.
    """
    cache_key = f"fakestore:all_products:{user_id}"
    queryset = Favorites.objects.filter(customer_id=user_id, active=True).order_by("-created_at")
    data = FavoritesSerializer(queryset, many=True).data
    cache.set(cache_key, data, CACHE_TIMEOUT)
    return data
