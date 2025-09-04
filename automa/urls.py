from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),       # http://127.0.0.1:8000/
    path("run/", views.run_proceso, name="run_proceso"),  # http://127.0.0.1:8000/run/
]
