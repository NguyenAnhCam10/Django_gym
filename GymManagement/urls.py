from django.contrib import admin
from django.urls import path, include
from GymApp.admin import admin_site
# Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Gym Management API",
        default_version='v1',
        description="API documentation for the gym management system",
        contact=openapi.Contact(email="nguyenanhcam10@gmail.com"),
        license=openapi.License(name="Nguyễn Anh Cam@2025"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('GymApp.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
