from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('run/', views.run_consulta, name='run'),  # endpoint AJAX
]
