from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from aiqfome.models import Favorites
from aiqfome.serializers import FavoritesSerializer
from utils.cache_utils import update_favorites_cache_for_user


class FavoritesRestView(viewsets.ModelViewSet):
    """Endpoint para gerenciar favoritos de produtos.

    Permite criar, listar, atualizar e desativar favoritos de produtos para o cliente autenticado.

    ### Payload para criação:
    ```json
        { "product_id": 3 }
    ```

    ### Resposta:
    ```json
        {
            "id": "uuid",
            "customer": "integer",
            "product_id": 3,
            "product_data": { ... },
            "active": true,
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ```
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FavoritesSerializer
    queryset = Favorites.objects.none()

    def get_object(self):
        pk = self.kwargs.get("pk")
        obj = get_object_or_404(Favorites, pk=pk)
        return obj

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @swagger_auto_schema(
        tags=["Favorites"],
        operation_summary="List active favorites",
        operation_description="Retrieve a list of active favorite products for the authenticated user.",
    )
    def list(self, request, *args, **kwargs):
        cache_key = f"fakestore:all_products:{request.user.id}"
        data = cache.get(cache_key)
        if not data:
            data = update_favorites_cache_for_user(request.user.id)

        return Response(data)

    @swagger_auto_schema(
        tags=["Favorites"],
        operation_summary="Create a new favorite",
        operation_description="Add a new product to the authenticated user's favorites.",
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        transaction.on_commit(lambda: update_favorites_cache_for_user(request.user.id))

        return response

    @swagger_auto_schema(
        tags=["Favorites"],
        operation_summary="Retrieve a favorite by ID",
        operation_description="Retrieve details of a favorite product by its ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.customer != request.user and not request.user.is_superuser:
            raise PermissionDenied(
                {"detail": "You do not have permission to perform this action."}
            )
        if instance.active is False:
            return Response(
                {"detail": "This favorite has been deactivated."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Favorites"],
        operation_summary="Deactivate a favorite",
        operation_description="Deactivate (soft delete) a favorite product for the authenticated user.",
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.customer != request.user and not request.user.is_superuser:
            return PermissionDenied(
                {"detail": "You do not have permission to perform this action."}
            )

        instance.active = False
        instance.save()

        transaction.on_commit(lambda: update_favorites_cache_for_user(request.user.id))

        return Response(status=status.HTTP_204_NO_CONTENT)
