from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .selenium_script import ejecutar_consulta


@csrf_exempt
def run_consulta(request):
    """
    Vista que recibe un número de documento por POST,
    lo pasa al script de Selenium y devuelve resultados en JSON.
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
        resultado = ejecutar_consulta(numero_doc)
        return JsonResponse({
            "status": "ok",
            "msg": f"✅ Consulta finalizada para {numero_doc}",
            "capturas": resultado.get("capturas", []),
            "archivos": resultado.get("archivos", [])
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "msg": f"❌ Error en la consulta: {str(e)}"
        }, status=500)


def index(request):
    """
    Renderiza la página principal con el formulario de consulta.
    """
    return render(request, "index.html")
