import os
import time
import sys
from docx import Document
from docx.shared import Inches
from docx.enum.section import WD_ORIENT
from docx2pdf import convert
from PyPDF2 import PdfMerger

# =======================
# CONFIGURACIÓN INICIAL
# =======================
sys.stdout.reconfigure(encoding='utf-8')

# Carpeta donde están las capturas y se generarán los PDFs
carpeta_capturas = r"C:\Users\Edinson\Desktop\TODO\CODIGOS\14_CONSULTOR\V7\seleniumweb\media\descargas"

# Nombre base del informe
numero_doc = "INFORME DE CONSULTAS"

salida_word = os.path.join(carpeta_capturas, f"{numero_doc}.docx")
salida_pdf = os.path.join(carpeta_capturas, f"{numero_doc}.pdf")
salida_final = os.path.join(carpeta_capturas, f"{numero_doc}_COMPLETO.pdf")

# =======================
# FUNCIÓN PRINCIPAL
# =======================
def generar_informe(carpeta):
    doc = Document()

    # Orientación horizontal
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width

    # Márgenes
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # Título principal
    doc.add_heading("INFORME DE CONSULTAS", level=1)

    # Orden de imágenes a incluir
    orden_capturas = [
        "ofac_final.png",
        "contaduria_final.png",
        "rues_evento_2.png",
        "rues_evento_5.png",
        "rues_evento_7.png",
        "rues_evento_9.png",
        "rues_evento_10.png",
        "rues_final.png"
    ]

    for i, archivo in enumerate(orden_capturas):
        img_path = os.path.join(carpeta, archivo)

        # 🔥 Si la imagen NO existe → no agregar nada (omitir por completo)
        if not os.path.exists(img_path):
            continue

        # Crear título a partir del nombre del archivo
        nombre_titulo = (
            os.path.splitext(archivo)[0]
            .replace("_final", "")
            .replace("_", " ")
            .upper()
        )

        doc.add_heading(nombre_titulo, level=2)

        # Insertar imagen
        try:
            doc.add_picture(img_path, width=Inches(10))
        except Exception as e:
            print(f"[ERROR] No se pudo insertar {img_path}: {e}")

        # Agregar salto de página excepto en la última
        if i < len(orden_capturas) - 1:
            doc.add_page_break()

    # Guardar Word
    doc.save(salida_word)
    print(f"[OK] Informe Word creado en:\n{salida_word}")

    # Convertir a PDF
    try:
        convert(salida_word, salida_pdf)
        print(f"[OK] Informe PDF generado en:\n{salida_pdf}")
    except Exception as e:
        print(f"[ERROR] No se pudo convertir a PDF: {e}")
        return

    # Esperar a que el PDF exista y no esté vacío
    for _ in range(10):
        if os.path.exists(salida_pdf) and os.path.getsize(salida_pdf) > 1000:
            break
        time.sleep(1)

    # =======================
    # COMBINAR PDFs
    # ========================
    try:
        pdfs_numericos = []

        # Buscar PDFs con nombres numéricos para combinarlos
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith(".pdf") and archivo != f"{numero_doc}.pdf":
                nombre = os.path.splitext(archivo)[0]
                if nombre.isdigit() or nombre.split("_")[0].isdigit():
                    pdfs_numericos.append(os.path.join(carpeta, archivo))

        if not pdfs_numericos:
            print("No se encontró ningún PDF numérico para combinar.")
            return

        # Ordenar por número
        pdfs_numericos.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split("_")[0]))

        # Combinar
        merger = PdfMerger()
        merger.append(salida_pdf)

        for pdf in pdfs_numericos:
            merger.append(pdf)

        merger.write(salida_final)
        merger.close()

        print(f"[OK] PDF combinado generado en:\n{salida_final}")

    except Exception as e:
        print(f"[ERROR] al combinar PDFs: {e}")


# =======================
# EJECUCIÓN
# =======================
if __name__ == "__main__":
    if not os.path.exists(carpeta_capturas):
        print(f"La carpeta {carpeta_capturas} no existe. Verifica la ruta.")
    else:
        generar_informe(carpeta_capturas)
