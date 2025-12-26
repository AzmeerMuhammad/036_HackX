"""
URL configuration for SafeSpace project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/journal/', include('apps.journal.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/professionals/', include('apps.professionals.urls')),
    path('api/consent/', include('apps.consent.urls')),
    path('api/history/', include('apps.history.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

