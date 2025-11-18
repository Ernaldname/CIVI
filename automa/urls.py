from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("run_consulta/", views.run_consulta, name="run_consulta"),
    path("descargas/", views.listar_archivos, name="listar_archivos"),
    path("descargas/eliminar/", views.eliminar_archivos, name="eliminar_archivos"),
    path("descargar_informe/", views.generar_y_descargar_pdf, name="descargar_informe"),

    # ✅ REFERENCIA CORRECTA
    path("listar_archivos_json/", views.listar_archivos_json, name="listar_archivos_json"),
]
