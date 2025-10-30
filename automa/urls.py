from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),                     # Página principal
    path("run_consulta/", views.run_consulta, name="run_consulta"),  # Endpoint JSON
    path("descargas/", views.listar_archivos, name="listar_archivos"),  # Listar archivos
    path("descargas/eliminar/", views.eliminar_archivos, name="eliminar_archivos"), # Eliminar archivos
]
