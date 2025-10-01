from django.contrib import admin
from django.urls import path, include  # ← aquí incluyes include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("automa.urls")),
]

# ✅ Esto permite servir archivos de /media/ en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
