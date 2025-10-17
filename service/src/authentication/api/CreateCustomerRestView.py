from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from authentication.models import Customer
from authentication.serializers import CustomerSerializer


class CreateCustomerRestView(viewsets.ModelViewSet):
    """Endpoint para registrar um novo usuário.

    Payload:
    ```json
        {
            "first_name": "string",
            "last_name": "string",
            "username": "string",
            "password": "string",
            "email": "string",
        }
    ```
    """

    permission_classes = [AllowAny]
    queryset = Customer.objects.all().order_by("-date_joined")
    serializer_class = CustomerSerializer
    http_method_names = ["post"]

    @swagger_auto_schema(
        tags=["Customers"],
        operation_summary="Create a new profile",
        operation_description="Register a new user profile.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
