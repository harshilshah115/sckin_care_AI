"""
URL configuration for AI Skincare Assistant project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/scan/', include('apps.skincare_analysis.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/history/', include('apps.history.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
