from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, 
                                            TokenVerifyView)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from authentication.api import CreateProfileRestView, ProfileRestView

schema_view = get_schema_view(
    openapi.Info(
        title="Armored Django API",
        default_version="v1",
        description="API documentation for the Armored Django project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@armoreddjango.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/login/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
if not settings.PRODUCTION:   
    urlpatterns += [
        path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

router = DefaultRouter(trailing_slash=False)
router.register(
    "api/register/", CreateProfileRestView, basename="CreateProfileRestView"
)
router.register("api/profile", ProfileRestView, basename="ProfileRestView")

urlpatterns += router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)