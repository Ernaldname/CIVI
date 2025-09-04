import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException

# -----------------------------
# 🚀 Función principal Selenium
# -----------------------------
def ejecutar_proceso(NUMERO_DOCUMENTO):
    BASE_DIR = os.getcwd()
    DOWNLOAD_PATH = os.path.join(BASE_DIR, "media", "descargas")
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")  # ⚠️ prueba primero visible
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    logging.basicConfig(
        filename="errores.log",
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Resultados acumulados
    capturas, archivos = [], []

    # -----------------------------
    # 🔧 Utilidades
    # -----------------------------
    def tomar_captura(nombre):
        path = os.path.join(DOWNLOAD_PATH, f"{nombre}.png")
        driver.save_screenshot(path)
        capturas.append(path)
        print(f"📸 Captura guardada en: {path}")

    def esperar_elemento(metodo, selector, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((metodo, selector))
        )

    def esperar_clickable(selector, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )

    def manejar_descarga(nombre, timeout=30):
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
        logging.warning(f"{nombre} - Tiempo de espera agotado, sin descargas")
        return None

    def aceptar_alerta_si_existe(pagina):
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

    # -----------------------------
    # 🌐 Procesar cada página
    # -----------------------------
    def procesar_ofac():
        try:
            driver.get("https://sanctionssearch.ofac.treas.gov/")
            tomar_captura("ofac_inicio")

            input_box = esperar_elemento(By.CSS_SELECTOR, "#ctl00_MainContent_txtLastName")
            input_box.clear()
            input_box.send_keys(str(NUMERO_DOCUMENTO))
            input_box.send_keys(Keys.ENTER)

            time.sleep(3)
            tomar_captura("ofac_resultado")
            # 👉 Si hubiera descarga:
            # manejar_descarga("ofac")

        except Exception as e:
            logging.error(f"OFAC error: {e}")

    def procesar_contraloria():
        try:
            driver.get("https://www.contraloria.gov.co/web/guest/persona-juridica")
            iframe = esperar_elemento(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframe)

            input_box = esperar_elemento(By.XPATH, "//input[@type='text']")
            input_box.clear()
            input_box.send_keys(str(NUMERO_DOCUMENTO))
            input_box.send_keys(Keys.TAB)
            input_box.send_keys(Keys.ENTER)

            time.sleep(5)
            tomar_captura("contraloria_resultado")
            manejar_descarga("contraloria")

            driver.switch_to.default_content()

        except Exception as e:
            logging.error(f"Contraloría error: {e}")

    def procesar_policia():
        try:
            driver.get("https://antecedentes.policia.gov.co:7005/WebJudicial/")
            aceptar_alerta_si_existe("policia")

            input_box = esperar_elemento(By.CSS_SELECTOR, "#cedulaInput")
            input_box.clear()
            input_box.send_keys(str(NUMERO_DOCUMENTO))
            input_box.send_keys(Keys.TAB)
            input_box.send_keys(Keys.ENTER)

            time.sleep(10)  # dejar que procese
            tomar_captura("policia_resultado")

        except Exception as e:
            logging.error(f"Policía error: {e}")

    # -----------------------------
    # ▶️ Ejecutar todas
    # -----------------------------
    procesar_ofac()
    procesar_contraloria()
    procesar_policia()

    driver.quit()
    print("\n🚀 Proceso completado.")

    return {
        "capturas": [os.path.relpath(c, BASE_DIR) for c in capturas],
        "archivos": [os.path.relpath(a, BASE_DIR) for a in archivos]
    }
