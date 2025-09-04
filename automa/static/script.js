// ======= LÓGICA DE AUDIO =======

// Reproducir audio al hacer clic en cualquier botón con data-audio
document.querySelectorAll('button[data-audio]').forEach(btn => {
    btn.addEventListener('click', () => {
        const audioId = btn.getAttribute('data-audio');
        const audio = document.getElementById(audioId);
        if (audio) {
            audio.currentTime = 0;
            audio.play();
        }
    });
});

// Pausar todos los audios al hacer clic en el botón "SILENCIAR"
document.getElementById('pausar-todos').addEventListener('click', () => {
    document.querySelectorAll('audio').forEach(audio => {
        audio.pause();
        audio.currentTime = 0;
    });
});

// ======= LÓGICA DE CARRERA CON META =======

// Configuración
const pista = document.getElementById('pista');
const pistaLength = 270;                // longitud de la pista (sin contar meta)
const car1 = '<span class="red">🍕</span>';
const car2 = '<span class="blue">🍳</span>';
const meta = ' '.repeat(pistaLength) + '🏁🏁*** META ***🏁🏁';
const velocidad = 50;                 // ms por frame
let pos1 = 0, pos2 = 0;                // posiciones iniciales
let ganador = null;

// Función scroll automático
function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}

// Mostrar pista en cada frame
function mostrarPista() {
    const line1 = ' '.repeat(pos1) + car1 + meta.slice(pos1 + car1.length);
    const line2 = ' '.repeat(pos2) + car2 + meta.slice(pos2 + car2.length);
    pista.innerHTML = line1 + '\n' + line2;
    scrollToBottom(pista);
}

// Animar carrera
function animarCarrera() {
    if (ganador) return; // si ya hay ganador, no seguir

    // Avance aleatorio: cada carro puede avanzar 0, 1 o 2 pasos
    pos1 += Math.floor(Math.random() * 4);
    pos2 += Math.floor(Math.random() * 4);

    mostrarPista();

    // Revisar ganador
    if (pos1 >= pistaLength) {
        ganador = "PIPSHA 🍕";
        pista.innerHTML += `\n\n🏆 Ganador: ${ganador}`;
        return;
    }
    if (pos2 >= pistaLength) {
        ganador = "WEBO 🍳";
        pista.innerHTML += `\n\n🏆 Ganador: ${ganador}`;
        return;
    }

    // Seguir animando
    setTimeout(animarCarrera, velocidad);
}

// Iniciar carrera
function carrera() {
    pos1 = 0;
    pos2 = 0;
    ganador = null;
    mostrarPista();
    animarCarrera();
}


