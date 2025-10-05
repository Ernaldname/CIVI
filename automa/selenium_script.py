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

# -----------------------------
# 📁 Configuración de entorno
# -----------------------------
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

# -----------------------------
# 🔧 Funciones utilitarias
# -----------------------------
def tomar_captura(driver, pagina, evento="inicio"):
    """Guarda captura de pantalla en la carpeta /media/descargas."""
    nombre_archivo = f"{pagina}_{evento}.png"
    ruta_absoluta = os.path.join(DOWNLOAD_PATH, nombre_archivo)
    driver.save_screenshot(ruta_absoluta)
    ruta_relativa = f"/media/descargas/{nombre_archivo}"
    capturas.append(ruta_relativa)
    print(f"📸 Captura guardada: {ruta_absoluta}")


def esperar_elemento(driver, metodo, selector, timeout=10):
    """Espera que un elemento esté presente en el DOM."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((metodo, selector))
    )


def esperar_clickable(driver, selector, timeout=10):
    """Espera que un elemento sea clickeable."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )


def aceptar_alerta_si_existe(driver, pagina):
    """Detecta y acepta alertas del navegador si aparecen."""
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alerta = driver.switch_to.alert
        print(f"⚠️ Alerta detectada en {pagina}, aceptando...")
        alerta.accept()
        time.sleep(1)
    except NoAlertPresentException:
        pass
    except Exception as e:
        logging.warning(f"{pagina} - Error al manejar alerta: {e}")


def manejar_iframe(driver, config, pagina):
    """Cambia al iframe si está configurado."""
    if not config.get("iframe_tag"):
        return
    try:
        iframe = esperar_elemento(driver, By.TAG_NAME, config["iframe_tag"])
        driver.switch_to.frame(iframe)
    except Exception as e:
        logging.error(f"{pagina} - Iframe no encontrado: {e}")
        raise


def ejecutar_evento_extra(driver, pagina, evento, index):
    """Ejecuta eventos adicionales como clics, scrolls o zoom."""
    tipo = evento["tipo"]
    try:
        if tipo == "scroll":
            driver.execute_script(f"window.scrollBy(0, {evento['valor']});")
        elif tipo == "zoom":
            driver.execute_script(f"document.body.style.zoom = '{evento['valor']}';")
        elif tipo == "espera_y_click":
            contenedor = esperar_elemento(driver, By.CSS_SELECTOR, evento.get("contenedor", "body"))
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, evento["selector"]))
            )
            elemento = contenedor.find_element(By.CSS_SELECTOR, evento["selector"])
            driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, evento["selector"])))
            elemento.click()
        elif tipo == "click":
            esperar_clickable(driver, evento["selector"]).click()
        elif tipo == "teclado":
            input_el = esperar_elemento(driver, By.CSS_SELECTOR, evento["selector"])
            input_el.send_keys(evento["tecla"])
        time.sleep(1)
        tomar_captura(driver, pagina, f"evento_{index}")
    except Exception as e:
        logging.warning(f"{pagina} - Evento {index} ({tipo}) no ejecutado: {e}")


def mensaje_captcha_presente(driver):
    """Verifica si aparece el mensaje del captcha."""
    try:
        elemento = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#j_idt10 > div > ul > li > span"))
        )
        return "Captcha" in elemento.text or "seleccionar las imagenes" in elemento.text
    except TimeoutException:
        return False


def procesar_input(driver, config, pagina):
    """Escribe el documento en el campo configurado y maneja TAB/ENTER."""
    metodo = By.XPATH if config["input_selector"].startswith("//") else By.CSS_SELECTOR
    try:
        input_box = esperar_elemento(driver, metodo, config["input_selector"])
        input_box.clear()
        input_box.send_keys(str(NUMERO_DOCUMENTO))

        tomar_captura(driver, pagina, "despues_input")

        for i, tecla in enumerate(config["eventos_teclado"]):
            if tecla == Keys.TAB:
                input_box.send_keys(Keys.TAB)
                time.sleep(1)
                try:
                    focused = driver.switch_to.active_element
                    focused.click()
                    print("🖱️ Clic realizado en el elemento enfocado por TAB.")
                except Exception as e:
                    logging.warning(f"{pagina} - No se pudo hacer clic tras TAB: {e}")
            else:
                if tecla == Keys.ENTER:
                    print("⏳ Esperando antes de enviar ENTER...")
                    time.sleep(2)
                input_box.send_keys(tecla)
                time.sleep(1)

    except Exception as e:
        logging.error(f"{pagina} - Error al escribir input: {e}")
        raise


def manejar_descarga(pagina, timeout=30):
    """Espera la descarga de un archivo en la carpeta destino."""
    print("⏳ Esperando descarga...")
    before = set(os.listdir(DOWNLOAD_PATH))
    end_time = time.time() + timeout
    while time.time() < end_time:
        after = set(os.listdir(DOWNLOAD_PATH))
        new_files = after - before
        if new_files:
            archivo = new_files.pop()
            ruta = os.path.join(DOWNLOAD_PATH, archivo)
            archivos.append(ruta)
            print(f"✅ Archivo descargado: {ruta}")
            return ruta
        time.sleep(1)
    logging.warning(f"{pagina} - Tiempo agotado sin descargas")
    return None

# -----------------------------
# 🌐 Procesamiento principal
# -----------------------------
def procesar_pagina(driver, pagina, config):
    print(f"\n📌 Procesando: {pagina}")

    if pagina == "policia":
        intentos = 0
        max_intentos = 10

        while intentos < max_intentos:
            driver.get(config["url"])
            aceptar_alerta_si_existe(driver, pagina)
            manejar_iframe(driver, config, pagina)

            for i, evento in enumerate(config.get("extra_eventos", []), start=1):
                ejecutar_evento_extra(driver, pagina, evento, i)

            try:
                esperar_elemento(driver, By.CSS_SELECTOR, config["input_selector"], timeout=3)
                procesar_input(driver, config, pagina)
                time.sleep(config.get("espera_post_input", 1))
                if not mensaje_captcha_presente(driver):
                    print("✅ Documento procesado correctamente.")
                    break
                else:
                    print("❌ Captcha no resuelto. Reintentando...")
                    tomar_captura(driver, pagina, f"captcha_error_{intentos}")
            except Exception as e:
                print(f"⚠️ Error al procesar intento {intentos}: {e}")

            intentos += 1
            driver.refresh()
            time.sleep(2)

        if intentos == max_intentos:
            logging.error(f"{pagina} - Excedidos los intentos máximos ({max_intentos})")

    if config.get("descargar"):
        manejar_descarga(pagina)
    if config.get("captura_pantalla"):
        tomar_captura(driver, pagina, "final")

    print(f"🔹 Finalizado: {pagina}")

# -----------------------------
# 🌍 Configuración de páginas
# -----------------------------
paginas = {

    "policia": {
        "url": "https://antecedentes.policia.gov.co:7005/WebJudicial/",
        "iframe_tag": None,
        "input_selector": "#cedulaInput",
        "eventos_teclado": [Keys.TAB, Keys.ENTER],
        "extra_eventos": [
            {"tipo": "espera_y_click", "contenedor": "#aceptaOption > tbody", "selector": "#aceptaOption\\:0"},
            {"tipo": "espera_y_click", "selector": "#continuarBtn"},
            {"tipo": "espera_y_click", "selector": "#j_idt17 > span"}
        ],
        "espera_post_input": 10,
        "descargar": False,
        "captura_pantalla": True
    },
    "contaduria": {
        "url": "https://eris.contaduria.gov.co/BDME/",
        "iframe_tag": None,
        "extra_eventos": [
            {"tipo": "zoom", "valor": 0.8},
            {"tipo": "scroll", "valor": 100},
            {"tipo": "retraso", "valor": 10},
            {"tipo": "click", "selector": "#panelMenu > ul > li:nth-child(1) > a"},
            {"tipo": "click", "selector": "body > div.gwt-DialogBox > div > table > tbody > tr.dialogMiddle > td.diaslogMiddleCenter > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > input"},
            {"tipo": "escribir", "selector": "body > div.gwt-DialogBox > div > table > tbody > tr.dialogMiddle > td.dialogMiddleCenter > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > input", "texto": "66860241"},
            {"tipo": "click", "selector": "body > div.gwt-DialogBox > div > table > tbody > tr.dialogMiddle > td.dialogMiddleCenter > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > input"},
            {"tipo": "escribir", "selector": "body > div.gwt-DialogBox > div > table > tbody > tr.dialogMiddle > td.dialogMiddleCenter > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > input", "texto": "9610845"},
            {"tipo": "click", "selector": "body > div.gwt-DialogBox > div > table > tbody > tr.dialogMiddle > td.dialogMiddleCenter > div > table > tbody > tr:nth-child(5) > td > button"},
            {"tipo": "click", "selector": "#panelPrincipal > div > div > div > div > div:nth-child(2) > form > div:nth-child(1) > div > select"},
            {"tipo": "click", "selector": "#panelPrincipal > div > div > div > div > div:nth-child(2) > form > div:nth-child(1) > div > select > option:nth-child(2)"},
            {"tipo": "click", "selector": "#panelPrincipal > div > div > div > div > div:nth-child(2) > form > div:nth-child(2) > div > input"},
            {"tipo": "escribir", "selector": "#panelPrincipal > div > div > div > div > div:nth-child(2) > form > div:nth-child(2) > div > input", "texto": "{DOC}"},
            {"tipo": "click", "selector": "#panelPrincipal > div > div > div > div > div:nth-child(2) > form > div:nth-child(3) > div > select"},
            {"tipo": "click", "selector": "#panelPrincipal > div > div > div > div > div:nth-child(2) > form > div:nth-child(3) > div > select > option:nth-child(2)"},
            {"tipo": "teclado", "selector": "body", "tecla": Keys.TAB},
            {"tipo": "teclado", "selector": "body", "tecla": Keys.SPACE},
            {"tipo": "retraso", "valor": 10}
             ],
            "descargar": False,
            "captura_pantalla": True
            },

    "contraloria": {
        "url": "https://www.contraloria.gov.co/web/guest/persona-juridica",
        "iframe_tag": "iframe",
        "input_selector": "//input[@type='text']",
        "eventos_teclado": [Keys.TAB, Keys.ENTER],
        "descargar": True,
        "captura_pantalla": False
    },

    "rues": {
        "url": "https://www.rues.org.co",
        "iframe_tag": None,
        "input_selector": "#search",
        "eventos_teclado": [Keys.ENTER],
        "extra_eventos": [
            {"tipo": "zoom", "valor": 0.75},
            {"tipo": "click", "selector": "body > div.swal2-container.swal2-center.swal2-backdrop-show > div > button"},
            {"tipo": "scroll", "valor": 200}
        ],
        "descargar": True,
        "captura_pantalla": True
    },

    "ofac": {
        "url": "https://sanctionssearch.ofac.treas.gov/",
        "iframe_tag": None,
        "input_selector": "#ctl00_MainContent_txtLastName",
        "eventos_teclado": [Keys.ENTER],
        "extra_eventos": [
            {"tipo": "zoom", "valor": 0.7},
            {"tipo": "scroll", "valor": 30}
        ],
        "descargar": False,
        "captura_pantalla": True
        }
}

# -----------------------------
# 🚀 Punto de entrada
# -----------------------------
def ejecutar_consulta(numero_doc):
    """Ejecuta el proceso completo para un documento dado."""
    global NUMERO_DOCUMENTO, capturas, archivos
    capturas, archivos = [], []
    NUMERO_DOCUMENTO = numero_doc

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    try:
        for nombre, config in paginas.items():
            procesar_pagina(driver, nombre, config)
    finally:
        driver.quit()

    print("\n🚀 Proceso completado.")
    return {"capturas": capturas, "archivos": archivos}
