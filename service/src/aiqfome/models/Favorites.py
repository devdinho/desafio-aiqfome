import uuid

from django.db import models
from simple_history.models import HistoricalRecords

from authentication.models import Customer


class Favorites(models.Model):
    history = HistoricalRecords()

    id = models.UUIDField(
        "ID do Favorito", primary_key=True, default=uuid.uuid7, editable=False
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Cliente",
    )
    product_id = models.IntegerField(verbose_name="ID do Produto")

    product_data = models.JSONField(
        verbose_name="Dados do Produto",
        help_text="Dados do produto favorito em formato JSON",
    )

    active = models.BooleanField(default=True, verbose_name="Ativo")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f'Favorito: {self.product_data.get("title")} por {self.customer}'

    class Meta:
        verbose_name = "Produto Favorito"
        verbose_name_plural = "Produtos Favoritos"
        unique_together = ("customer", "product_id")
        indexes = [
            models.Index(fields=["customer", "active"], name="idx_customer_active")
        ]
