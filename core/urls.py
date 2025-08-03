# affiproductapi/urls.py (main project urls)

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.products.urls')),
    path('api/', include('apps.marketing.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Customize admin site
admin.site.site_header = "Affiliate Product API Administration"
admin.site.site_title = "Affiliate Product API Admin"
admin.site.index_title = "Welcome to Affiliate Product API Administration"