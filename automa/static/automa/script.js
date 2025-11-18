// ===============================================================
// 📄 ARCHIVO: script.js
// 💡 FUNCIÓN PRINCIPAL: Conectar el frontend con Django y animar la interfaz
// Contiene tres secciones principales:
//   1️⃣ Consulta AJAX a la vista Django (run_consulta)
//   2️⃣ Obtención del token CSRF para seguridad
//   3️⃣ Efectos visuales y animaciones de interfaz
// ===============================================================

// ======= 1️⃣ CONSULTA AJAX PRINCIPAL =======
// Esta función se ejecuta cuando el usuario hace clic en el botón de búsqueda.
// Envía el número de documento al servidor Django y espera una respuesta JSON.

async function buscarPN() {
    const numDoc = document.getElementById("numero_de_documento").value;

    if (!numDoc) {
        alert("Por favor ingresa un número de documento.");
        return;
    }

    // 👉 MUESTRA LOADER
    document.getElementById("loader").classList.remove("oculto");

    try {
        const response = await fetch("/run_consulta/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken()
            },
            body: "numero=" + encodeURIComponent(numDoc)
        });

        const text = await response.text();
        let data;

        try {
            data = JSON.parse(text);
        } catch {
            console.error("⚠️ Respuesta del servidor (no JSON):", text);
            alert("❌ El servidor devolvió una respuesta inesperada.");
            return;
        }

        const resultados = document.getElementById("resultados");
        resultados.innerHTML = "";

        if (data.status === "ok") {
            alert("✅ Proceso completado correctamente.");
            if (data.tiempo) {
                resultados.innerHTML += `<p>⏱ Tiempo de ejecución: ${data.tiempo}</p>`;
            }
        } else {
            alert("⚠️ " + data.msg);
        }

    } catch (error) {
        alert("❌ Error al procesar la consulta: " + error);

    } finally {
        // 👉 OCULTA LOADER SIEMPRE (éxito o error)
        document.getElementById("loader").classList.add("oculto");
    }
}


// ======= 2️⃣ FUNCIÓN DE SEGURIDAD CSRF =======
// Django requiere que cada solicitud POST incluya un token CSRF.
// Esta función lo extrae de las cookies del navegador y lo devuelve.
function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name)) {
            return cookie.substring(name.length);
        }
    }
    return ""; // Si no lo encuentra, retorna vacío (fetch fallará en este caso)
}

// ======= 3️⃣ ANIMACIONES Y EFECTOS DE INTERFAZ =======
// Este bloque se ejecuta cuando el DOM termina de cargarse.
document.addEventListener("DOMContentLoaded", () => {
    // 🎬 Animación inicial del título principal
    const titulo = document.querySelector(".titulo.animado");
    if (titulo) {
        titulo.style.opacity = 0;
        titulo.style.transform = "scale(0.8)";
        setTimeout(() => {
            titulo.style.transition = "all 1s ease";
            titulo.style.opacity = 1;
            titulo.style.transform = "scale(1)";
        }, 300);
    }

    // ✨ Brillo dinámico en los botones con clase .boton-animado
    document.querySelectorAll(".boton-animado").forEach(btn => {
        btn.addEventListener("mouseover", () => {
            btn.style.boxShadow = "0 0 15px #5FA8D3"; // Efecto brillante
        });
        btn.addEventListener("mouseout", () => {
            btn.style.boxShadow = "0 2px 6px rgba(95, 168, 211, 0.25)"; // Efecto normal
        });
    });

    // 🔔 Resalta el borde del input si está vacío o lleno
    const inputDoc = document.getElementById("numero_de_documento");
    if (inputDoc) {
        inputDoc.addEventListener("input", () => {
            if (inputDoc.value.trim() === "") {
                inputDoc.style.borderColor = "#5FA8D3";
                inputDoc.style.animation = "pulse 0.5s infinite"; // Efecto animado
            } else {
                inputDoc.style.borderColor = "#1B4965";
                inputDoc.style.animation = "none"; // Quita la animación si ya hay texto
            }
        });
    }
});


// ===============================================================
// 📥 4️⃣ GENERAR Y DESCARGAR PDF CON LAS CAPTURAS SELECCIONADAS
// ===============================================================

async function generarPDF() {
    // Selecciona los checkboxes marcados (imágenes seleccionadas)
    const seleccionadas = Array.from(document.querySelectorAll("input[name='imagenes']:checked"))
        .map(cb => cb.value);

    if (seleccionadas.length === 0) {
        alert("⚠️ Debes seleccionar al menos una imagen para generar el informe.");
        return;
    }

    try {
        // Crea un objeto FormData y añade las imágenes seleccionadas
        const formData = new FormData();
        seleccionadas.forEach(img => formData.append("imagenes", img));

        // Envía la solicitud al backend
        const response = await fetch("/generar_pdf/", {
            method: "POST",
            headers: { "X-CSRFToken": getCSRFToken() },
            body: formData
        });

        if (!response.ok) throw new Error("Error al generar el PDF");

        // Convierte la respuesta (PDF binario) en un blob
        const blob = await response.blob();

        // Crea un enlace temporal para descargar el PDF
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "informe_capturas.pdf";
        document.body.appendChild(a);
        a.click();

        // Limpieza
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (error) {
        console.error("❌ Error generando PDF:", error);
        alert("❌ No se pudo generar el informe. Revisa la consola para más detalles.");
    }
}

