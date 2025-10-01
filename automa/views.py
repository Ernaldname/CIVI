from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
import os
import time

from .selenium_script import ejecutar_consulta


@csrf_exempt
def run_consulta(request):
    """
    Vista que recibe un número de documento por POST,
    lo pasa al script Selenium y devuelve resultados JSON.
    """
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "msg": "Método no permitido (usa POST)"
        }, status=405)

    numero_doc = request.POST.get("numero")
    if not numero_doc:
        return JsonResponse({
            "status": "error",
            "msg": "⚠️ Falta el número de documento"
        }, status=400)

    try:
        # 🕒 Medir tiempo de ejecución
        inicio = time.time()
        resultado = ejecutar_consulta(numero_doc)
        duracion = time.time() - inicio  # segundos

        # 🔄 Convertir rutas absolutas a URLs servibles
        capturas_rel = []
        for c in resultado.get("capturas", []):
            rel_path = c.replace(str(settings.MEDIA_ROOT), "")
            url = settings.MEDIA_URL + rel_path.replace("\\", "/").lstrip("/")
            capturas_rel.append(url)

        archivos_rel = []
        for a in resultado.get("archivos", []):
            rel_path = a.replace(str(settings.MEDIA_ROOT), "")
            url = settings.MEDIA_URL + rel_path.replace("\\", "/").lstrip("/")
            archivos_rel.append(url)

        return JsonResponse({
            "status": "ok",
            "msg": f"✅ Consulta finalizada para {numero_doc}",
            "tiempo": f"{duracion:.2f} segundos",
            "capturas": capturas_rel,
            "archivos": archivos_rel
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "msg": f"❌ Error en la consulta: {str(e)}"
        }, status=500)


def index(request):
    """Renderiza la página principal con el formulario."""
    return render(request, "automa/index.html")

