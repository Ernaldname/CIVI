from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.conf import settings
from docx import Document
from docx.shared import Inches
import os
import time
import tempfile
import pypandoc
import traceback

from .selenium_script import ejecutar_consulta


# ==========================================================
# 🖼️ Capturas específicas que se incluirán en el informe
# ==========================================================
CAPTURAS_INFORME = [
    "ofac_final.png",
    "contaduria_final.png",
    "ofac_final.png"
]


# ==========================================================
# 🔹 API: Ejecutar Selenium y generar PDF automáticamente
# ==========================================================
@csrf_exempt
def run_consulta(request):
    """
    Ejecuta el script Selenium, selecciona capturas específicas,
    genera un informe PDF y devuelve su URL pública.
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
        inicio = time.time()
        resultado = ejecutar_consulta(numero_doc)
        duracion = time.time() - inicio

        # 🔁 Filtrar solo las capturas deseadas
        capturas_seleccionadas = [
            c for c in resultado.get("capturas", [])
            if os.path.basename(c) in CAPTURAS_INFORME
        ]

        # 🧾 Crear documento Word temporal
        doc = Document()
        doc.add_heading(f"Informe de Consulta - {numero_doc}", level=1)
        doc.add_paragraph(f"Duración: {duracion:.2f} segundos")
        doc.add_paragraph("Capturas incluidas en este informe:\n")

        for ruta in capturas_seleccionadas:
            nombre = os.path.basename(ruta)
            if os.path.exists(ruta):
                doc.add_paragraph(nombre)
                doc.add_picture(ruta, width=Inches(5.5))
            else:
                doc.add_paragraph(f"⚠️ No se encontró la captura: {nombre}")

        # 📄 Guardar DOCX temporalmente
        tmp_dir = tempfile.mkdtemp()
        docx_path = os.path.join(tmp_dir, "informe.docx")
        pdf_path = os.path.join(tmp_dir, "informe.pdf")
        doc.save(docx_path)

        
        # 🔄 Convertir DOCX → PDF con pypandoc y ruta completa de wkhtmltopdf
        try:
            wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

            # 1️⃣ Convertir DOCX → HTML temporal
            html_path = os.path.join(tmp_dir, "informe.html")
            pypandoc.convert_file(docx_path, "html", outputfile=html_path, extra_args=["--standalone"])

            # 2️⃣ Convertir HTML → PDF usando wkhtmltopdf directamente
            os.system(f'"{wkhtmltopdf_path}" "{html_path}" "{pdf_path}"')
        
        except Exception as e:
            print("🧨 ERROR COMPLETO EN run_consulta():")
            print(traceback.format_exc())
            return JsonResponse({
            "status": "error",
            "msg": f"❌ Error generando PDF: {str(e)}"
            }, status=500)

        # 📂 Guardar el PDF final en /media/descargas/
        carpeta_salida = os.path.join(settings.MEDIA_ROOT, "descargas")
        os.makedirs(carpeta_salida, exist_ok=True)
        destino = os.path.join(carpeta_salida, f"informe_{numero_doc}.pdf")
        os.replace(pdf_path, destino)

        # 🌐 URL pública para el usuario
        url_pdf = settings.MEDIA_URL + f"descargas/informe_{numero_doc}.pdf"

        return JsonResponse({
            "status": "ok",
            "msg": f"✅ Consulta completada para {numero_doc}",
            "tiempo": f"{duracion:.2f} segundos",
            "informe_pdf": url_pdf
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "msg": f"❌ Error en la consulta: {str(e)}"
        }, status=500)


# ==========================================================
# 🔹 Página principal
# ==========================================================
def index(request):
    """Renderiza la página principal con el formulario."""
    return render(request, "automa/index.html")


# ==========================================================
# 🔹 Listar archivos en /media/descargas/
# ==========================================================
def listar_archivos(request):
    carpeta_descargas = os.path.join(settings.MEDIA_ROOT, "descargas")

    if not os.path.exists(carpeta_descargas):
        return render(request, "automa/listar.html", {
            "archivos": [],
            "error": "⚠️ La carpeta 'descargas' no existe."
        })

    archivos = []
    for nombre in os.listdir(carpeta_descargas):
        ruta_completa = os.path.join(carpeta_descargas, nombre)
        if os.path.isfile(ruta_completa):
            archivos.append({
                "nombre": nombre,
                "url": f"{settings.MEDIA_URL}descargas/{nombre}"
            })

    filtro = request.GET.get("filtro")
    if filtro:
        archivos = [a for a in archivos if filtro.lower() in a["nombre"].lower()]

    return render(request, "automa/listar.html", {"archivos": archivos})


# ==========================================================
# 🔹 Eliminar archivos seleccionados
# ==========================================================
@require_POST
def eliminar_archivos(request):
    seleccionados = request.POST.getlist("archivos")
    carpeta_descargas = os.path.join(settings.MEDIA_ROOT, "descargas")

    eliminados = []
    errores = []

    for nombre in seleccionados:
        ruta = os.path.join(carpeta_descargas, nombre)
        try:
            os.remove(ruta)
            eliminados.append(nombre)
        except Exception as e:
            errores.append(f"{nombre}: {str(e)}")

    mensaje = f"✅ {len(eliminados)} archivo(s) eliminado(s)."
    if errores:
        mensaje += f" ⚠️ {len(errores)} no se pudieron eliminar."

    archivos = []
    for nombre in os.listdir(carpeta_descargas):
        ruta_completa = os.path.join(carpeta_descargas, nombre)
        if os.path.isfile(ruta_completa):
            archivos.append({
                "nombre": nombre,
                "url": f"{settings.MEDIA_URL}descargas/{nombre}"
            })

    return render(request, "automa/listar.html", {
        "archivos": archivos,
        "mensaje": mensaje
    })
