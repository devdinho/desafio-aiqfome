from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from authentication.models import Profile
from authentication.serializers import ProfileSerializer


class CreateProfileRestView(viewsets.ModelViewSet):
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
    queryset = Profile.objects.all().order_by("-date_joined")
    serializer_class = ProfileSerializer
    http_method_names = ["post"]

    @swagger_auto_schema(
        tags=["Profiles"],
        operation_summary="Create a new profile",
        operation_description="Register a new user profile.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
