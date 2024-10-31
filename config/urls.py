from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularYAMLAPIView, SpectacularRedocView


schema_view = get_schema_view(
    openapi.Info(
        title="구름멍! API 문서",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path("swagger.json/", SpectacularJSONAPIView.as_view(), name="schema-json"),
    path("swagger.yaml/", SpectacularYAMLAPIView.as_view(), name="swagger-yaml"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema-json"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema-json"), name="redoc", ),
    path('api/', include('barameong.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)