from django.shortcuts import render
from django.http import JsonResponse
from .selenium_script import ejecutar_proceso

def index(request):   # 👈 ESTA función debe existir
    return render(request, "index.html")

def run_proceso(request):
    if request.method == "POST":
        numero = request.POST.get("numero")
        if numero:
            resultados = ejecutar_proceso(numero)
            return JsonResponse({
                "status": "ok",
                "msg": "Proceso completado",
                "capturas": [f"/{c}" for c in resultados["capturas"]],
                "archivos": [f"/{a}" for a in resultados["archivos"]],
            })
        return JsonResponse({"status": "error", "msg": "Número requerido"})
