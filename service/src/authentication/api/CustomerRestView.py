from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import MethodNotAllowed, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import Customer
from authentication.serializers import CustomerSerializer
from utils.cache_utils import update_favorites_cache_for_user


class CustomerRestView(viewsets.ModelViewSet):
    """Endpoint para registrar, editar, visualizar e apagar um usuário.

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

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.none()

    def get_object(self):
        pk = self.kwargs.get("pk")
        obj = get_object_or_404(Customer, pk=pk)
        return obj

    @swagger_auto_schema(
        tags=["Customers"],
        operation_summary="Retrieve self profile",
        operation_description="Retrieve the profile of the authenticated user.",
    )
    def list(self, request, *args, **kwargs):
        instance = Customer.objects.filter(id=request.user.id).first()
        if not instance:
            raise NotFound(detail="Customer not found")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(auto_schema=None)
    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="Create not allowed")

    @swagger_auto_schema(
        tags=["Customers"],
        operation_summary="Retrieve a profile by ID",
        operation_description="Retrieve the profile of a user by their ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=["Customers"],
        operation_summary="Update a profile by ID",
        operation_description="""Update the profile of a user by their ID.
        Users can only update their own profile unless they are superusers.""",
    )
    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(Customer, id=kwargs.get("pk"))

        if instance.id != request.user.id and not request.user.is_superuser:
            raise PermissionDenied(detail="You can only update your own profile!")

        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Customers"],
        operation_summary="Delete a profile by ID",
        operation_description="""Delete the profile of a user by their ID.
        Users can only delete their own profile unless they are superusers.""",
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id != request.user.id and not request.user.is_superuser:
            raise PermissionDenied(detail="You can only delete your own profile!")

        transaction.on_commit(
            lambda: update_favorites_cache_for_user(request.user.id, invalidate=True)
        )

        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Customers"],
        operation_summary="Partially update a profile by ID",
        operation_description="""Partially update the profile of a user by their ID.
        Users can only update their own profile unless they are superusers.""",
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id != request.user.id and not request.user.is_superuser:
            raise PermissionDenied(detail="You can only update your own profile!")

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
