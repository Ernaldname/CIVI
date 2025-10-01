// ======= CONSULTA AJAX =======
async function buscarPN() {
    const numDoc = document.getElementById("numero_de_documento").value;

    if (!numDoc) {
        alert("Por favor ingresa un número de documento.");
        return;
    }

    try {
        const response = await fetch("/run/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken()
            },
            body: "numero=" + encodeURIComponent(numDoc)
        });

        const data = await response.json();

        const resultados = document.getElementById("resultados");
        resultados.innerHTML = ""; // Limpiar antes

        if (data.status === "ok") {
            alert(data.msg);

            // Mostrar tiempo
            if (data.tiempo) {
                resultados.innerHTML += `<p>⏱ Tiempo de ejecución: ${data.tiempo}</p>`;
            }
        } else {
            alert(data.msg);
        }

    } catch (error) {
        alert("❌ Error al procesar la consulta: " + error);
    }
}

// ✅ Obtener CSRF token desde las cookies
function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name)) {
            return cookie.substring(name.length);
        }
    }
    return "";
}

// ======= ANIMACIONES =======
document.addEventListener("DOMContentLoaded", () => {
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

    // ✨ Brillo dinámico en botones
    document.querySelectorAll(".boton-animado").forEach(btn => {
        btn.addEventListener("mouseover", () => {
            btn.style.boxShadow = "0 0 15px #5FA8D3";
        });
        btn.addEventListener("mouseout", () => {
            btn.style.boxShadow = "0 2px 6px rgba(95, 168, 211, 0.25)";
        });
    });

    // 🔔 Resaltar borde del input si está vacío
    const inputDoc = document.getElementById("numero_de_documento");
    if (inputDoc) {
        inputDoc.addEventListener("input", () => {
            if (inputDoc.value.trim() === "") {
                inputDoc.style.borderColor = "#5FA8D3";
                inputDoc.style.animation = "pulse 0.5s infinite";
            } else {
                inputDoc.style.borderColor = "#1B4965";
                inputDoc.style.animation = "none";
            }
        });
    }
});
