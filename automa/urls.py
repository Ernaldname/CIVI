from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),       # 👈 ahora / carga el formulario
    path("run/", views.run_consulta, name="run_consulta"),
]
