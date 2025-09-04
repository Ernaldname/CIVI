from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),   # admin de Django
    path('', include('automa.urls')),  # 👈 aquí decimos: "todo lo demás lo maneja automa"
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('automa.urls')),
]

if settings.DEBUG:  # solo en desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
