import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoAlertPresentException,
    TimeoutException
)

# ===================================================
# 📁 CONFIGURACIÓN GENERAL
# ===================================================

BASE_DIR = os.getcwd()
DOWNLOAD_PATH = os.path.join(BASE_DIR, "media", "descargas")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

logging.basicConfig(
    filename="errores.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

capturas, archivos = [], []
NUMERO_DOCUMENTO = None


# ===================================================
# 🧰 FUNCIONES UTILITARIAS
# ===================================================

def tomar_captura(driver, pagina, evento="inicio"):
    """Guarda una captura de pantalla."""
    nombre = f"{pagina}_{evento}.png"
    ruta = os.path.join(DOWNLOAD_PATH, nombre)
    driver.save_screenshot(ruta)
    capturas.append(f"/media/descargas/{nombre}")
    print(f"📸 Captura: {ruta}")


def esperar(driver, metodo, selector, timeout=10, clickable=False):
    """Espera un elemento (presente o clickeable)."""
    try:
        cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
        return WebDriverWait(driver, timeout).until(cond((metodo, selector)))
    except TimeoutException:
        raise TimeoutException(f"Elemento no encontrado: {selector}")


def aceptar_alerta(driver, pagina):
    """Acepta alertas del navegador si existen."""
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alerta = driver.switch_to.alert
        print(f"⚠️ Alerta detectada en {pagina}, aceptando...")
        alerta.accept()
    except NoAlertPresentException:
        pass
    except Exception as e:
        logging.warning(f"{pagina} - Error al aceptar alerta: {e}")


def cambiar_iframe(driver, config, pagina):
    """Entra al iframe configurado."""
    iframe_tag = config.get("iframe_tag")
    if iframe_tag:
        try:
            iframe = esperar(driver, By.TAG_NAME, iframe_tag)
            driver.switch_to.frame(iframe)
        except Exception as e:
            logging.error(f"{pagina} - Error al cambiar a iframe: {e}")


def procesar_input(driver, config, pagina):
    """Escribe el número de documento en el input configurado."""
    selector = config.get("input_selector")
    if not selector:
        return
    metodo = By.XPATH if selector.startswith("//") else By.CSS_SELECTOR
    try:
        input_box = esperar(driver, metodo, selector)
        input_box.clear()
        input_box.send_keys(str(NUMERO_DOCUMENTO))
        tomar_captura(driver, pagina, "input")

        for tecla in config.get("eventos_teclado", []):
            input_box.send_keys(tecla)
            time.sleep(1)

    except Exception as e:
        logging.error(f"{pagina} - Error al procesar input: {e}")


def manejar_descarga(pagina, timeout=30):
    """Espera la descarga de un archivo."""
    print("⏳ Esperando descarga...")
    antes = set(os.listdir(DOWNLOAD_PATH))
    fin = time.time() + timeout

    while time.time() < fin:
        nuevos = set(os.listdir(DOWNLOAD_PATH)) - antes
        if nuevos:
            archivo = nuevos.pop()
            ruta = os.path.join(DOWNLOAD_PATH, archivo)
            archivos.append(ruta)
            print(f"✅ Archivo descargado: {ruta}")
            return ruta
        time.sleep(1)

    logging.warning(f"{pagina} - No se detectaron descargas")
    return None


def ejecutar_evento(driver, pagina, evento, index):
    """Ejecuta un evento (click, scroll, zoom, etc)."""
    tipo = evento["tipo"]
    try:
        if tipo == "scroll":
            driver.execute_script(f"window.scrollBy(0, {evento['valor']});")

        elif tipo == "zoom":
            driver.execute_script(f"document.body.style.zoom='{evento['valor']}';")

        elif tipo == "retraso":
            time.sleep(evento["valor"])

        elif tipo == "click":
            esperar(driver, By.CSS_SELECTOR, evento["selector"], clickable=True).click()

        elif tipo == "espera_y_click":
            esperar(driver, By.CSS_SELECTOR, evento["selector"], clickable=True).click()

        elif tipo == "click_recaptcha":
            print("🔍 Buscando reCAPTCHA...")
            iframe = esperar(driver, By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")
            driver.switch_to.frame(iframe)
            checkbox = esperar(driver, By.CSS_SELECTOR, "#recaptcha-anchor", clickable=True)
            driver.execute_script("arguments[0].click();", checkbox)
            driver.switch_to.default_content()
            print("✅ reCAPTCHA clickeado")

        elif tipo == "escribir":
            el = esperar(driver, By.CSS_SELECTOR, evento["selector"])
            texto = evento["texto"].replace("{DOC}", str(NUMERO_DOCUMENTO))
            el.clear()
            el.send_keys(texto)

        elif tipo == "teclado":
            el = esperar(driver, By.CSS_SELECTOR, evento["selector"])
            el.send_keys(evento["tecla"])

        elif tipo == "captura":
            tomar_captura(driver, pagina, evento.get("descripcion", f"evento_{index}"))

        time.sleep(1)
        if tipo not in ("retraso", "captura"):
            tomar_captura(driver, pagina, f"evento_{index}")

    except Exception as e:
        logging.warning(f"{pagina} - Error en evento {index} ({tipo}): {e}")


# ===================================================
# 🌍 PROCESAMIENTO DE PÁGINAS
# ===================================================

def procesar_pagina(driver, pagina, config):
    print(f"\n📌 Procesando página: {pagina}")
    try:
        driver.get(config["url"])
        aceptar_alerta(driver, pagina)
        cambiar_iframe(driver, config, pagina)

        procesar_input(driver, config, pagina)

        for i, evento in enumerate(config.get("extra_eventos", []), start=1):
            ejecutar_evento(driver, pagina, evento, i)

        if config.get("descargar"):
            manejar_descarga(pagina)

        if config.get("captura_pantalla"):
            tomar_captura(driver, pagina, "final")

        if config.get("retraso"):
            time.sleep(config["retraso"])

        driver.switch_to.default_content()

    except Exception as e:
        logging.error(f"{pagina} - Error general: {e}")
    finally:
        print(f"✅ Página finalizada: {pagina}")


# ===================================================
# 🌐 CONFIGURACIÓN DE PÁGINAS
# ===================================================

paginas = {
    "rues": {
        "url": "https://www.rues.org.co",
        "input_selector": "#search",
        "eventos_teclado": [Keys.ENTER],
        "extra_eventos": [
            {"tipo": "zoom", "valor": 0.75},
            {"tipo": "click", "selector": "body > div.swal2-container.swal2-center.swal2-backdrop-show > div > button"},
            {"tipo": "captura", "descripcion": "cerrar_popup"},
            {"tipo": "click", "selector": "#app > main > div > div > div > div > div.row.card-result.p-4 > div.col.font-rues--small.d-flex.flex-column.justify-content-end > div > div:nth-child(1) > a"},
            {"tipo": "click", "selector": "#detail-tabs-tab-pestana_general > span"},
            {"tipo": "captura", "descripcion": "pestana_general"},
            {"tipo": "click", "selector": "#detail-tabs-tab-pestana_economica > span"},
            {"tipo": "click", "selector": "#detail-tabs-tab-pestana_representante > span"},
            {"tipo": "click", "selector": "#detail-tabs-tab-pestana_establecimientos > span"},
            {"tipo": "scroll", "valor": 200},
            {"tipo": "captura", "descripcion": "scroll_final"}
        ],
        "descargar": True,
        "captura_pantalla": True
    },
    "ofac": {
        "url": "https://sanctionssearch.ofac.treas.gov/",
        "input_selector": "#ctl00_MainContent_txtLastName",
        "eventos_teclado": [Keys.ENTER],
        "extra_eventos": [
            {"tipo": "zoom", "valor": 0.7},
            {"tipo": "scroll", "valor": 30}
        ],
        "descargar": False,
        "captura_pantalla": True
    },
    "contraloria": {
        "url": "https://www.contraloria.gov.co/web/guest/persona-juridica",
        "iframe_tag": "iframe",
        "input_selector": "//input[@type='text']",
        "eventos_teclado": [Keys.TAB, Keys.ENTER],
        "descargar": True
    },
    "contaduria": {
        "url": "https://eris.contaduria.gov.co/BDME/",
        "extra_eventos": [
            {"tipo": "zoom", "valor": 0.8},
            {"tipo": "scroll", "valor": 100},
            {"tipo": "retraso", "valor": 10},
            {"tipo": "click", "selector": "#panelMenu > ul > li:nth-child(1) > a"},
            {"tipo": "click", "selector": "#panelPrincipal > div > div > div > div > div:nth-child(2) > form > div:nth-child(2) > div > input"},
            {"tipo": "escribir", "selector": "#panelPrincipal > div > div > div > div > div:nth-child(2) > form > div:nth-child(2) > div > input", "texto": "{DOC}"},
            {"tipo": "click_recaptcha"},
            {"tipo": "retraso", "valor": 10}
        ],
        "captura_pantalla": True
    }
}


# ===================================================
# 🚀 FUNCIÓN PRINCIPAL
# ===================================================

def ejecutar_consulta(numero_doc):
    """Ejecuta la automatización completa."""
    global NUMERO_DOCUMENTO, capturas, archivos
    NUMERO_DOCUMENTO = numero_doc
    capturas, archivos = [], []

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_PATH,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    try:
        for nombre, config in paginas.items():
            procesar_pagina(driver, nombre, config)
    finally:
        driver.quit()

    print("\n✅ Proceso completado correctamente.")
    return {"capturas": capturas, "archivos": archivos}
