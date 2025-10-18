from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.test import APIRequestFactory

from aiqfome.models import Favorites
from utils.FakeStoreProxyViewSet import FakeStoreProxyViewSet


class FavoritesSerializer(serializers.ModelSerializer):
    """Serializer para o modelo de favoritos.

    ### Utilizado para converter objetos de favoritos em JSON e vice-versa.

    Campos:
    - id: Identificador único do favorito.
    - customer: Cliente associado ao favorito.
    - product_id: Produto associado ao favorito.
    - product_data: Dados do produto em formato JSON.
    - active: Indica se o favorito está ativo.
    - created_at: Data e hora de criação do favorito.
    - updated_at: Data e hora da última atualização do favorito.
    """

    product_id = serializers.IntegerField()

    class Meta:
        model = Favorites
        fields = (
            "id",
            "customer",
            "product_id",
            "product_data",
            "active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "customer",
            "product_data",
            "created_at",
            "updated_at",
            "active",
        )

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        product_id = validated_data["product_id"]

        factory = APIRequestFactory()
        fake_get_request = factory.get(f"/products/{product_id}/")

        view = FakeStoreProxyViewSet.as_view({"get": "retrieve"})
        response = view(fake_get_request, pk=product_id)

        if response.status_code != 200:
            raise NotFound("Produto não encontrado.")

        product_data = response.data
        product_data.pop("id", None)
        favorite, create = Favorites.objects.get_or_create(
            customer=user,
            product_id=product_id,
            defaults={"product_data": product_data, "active": True},
        )
        if favorite and favorite.active and not create:
            raise serializers.ValidationError("Produto já está nos favoritos.")

        if not create:
            favorite.active = True
            favorite.product_data = product_data
            favorite.save()

        return favorite
