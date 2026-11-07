// =========================================================
// CRONÓMETRO DE LA CAGADA (registrar)
// El estado se guarda en localStorage y se recupera de los
// campos ocultos, para que no se pierda por un error del
// formulario, una recarga o el desvío a crear ubicación.
// Solo se borra al reiniciar o al registrar la cagada.
// =========================================================

document.addEventListener('DOMContentLoaded', function () {
    const formulario = document.getElementById('form-registrar-cagada');

    const btnIniciar = document.getElementById('btn-iniciar');
    const btnTerminar = document.getElementById('btn-terminar');
    const btnReiniciar = document.getElementById('btn-reiniciar');
    const btnRegistrar = document.getElementById('btn-registrar');

    const estado = document.getElementById('estado');
    const horaInicio = document.getElementById('hora-inicio');
    const horaFinal = document.getElementById('hora-final');
    const temporizador = document.getElementById('temporizador');

    const campoInicio = document.getElementById('id_hora_inicio_cagada');
    const campoFinal = document.getElementById('id_hora_final_cagada');

    if (
        !formulario ||
        !btnIniciar ||
        !btnTerminar ||
        !btnReiniciar ||
        !btnRegistrar ||
        !estado ||
        !horaInicio ||
        !horaFinal ||
        !temporizador ||
        !campoInicio ||
        !campoFinal
    ) {
        return;
    }

    // Una clave por usuario, por si varias personas usan el mismo navegador
    const CLAVE_CRONOMETRO =
        `proyectokk_cronometro_${formulario.dataset.usuario || 'anonimo'}`;

    let inicioTimestamp = null;
    let intervalo = null;

    // ---------------------------------------------------------
    // Formatos
    // ---------------------------------------------------------

    function formatearHora(fecha) {
        return fecha.toLocaleTimeString('es-CO', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    }

    function formatearFechaDjango(fecha) {
        const pad = (n) => String(n).padStart(2, '0');
        const año = fecha.getFullYear();
        const mes = pad(fecha.getMonth() + 1);
        const dia = pad(fecha.getDate());
        const hora = pad(fecha.getHours());
        const minuto = pad(fecha.getMinutes());
        const segundo = pad(fecha.getSeconds());

        // Desfase respecto a UTC (Colombia: -05:00)
        const desfaseMinutos = -fecha.getTimezoneOffset();
        const signo = desfaseMinutos >= 0 ? '+' : '-';
        const desfaseHoras = pad(Math.floor(Math.abs(desfaseMinutos) / 60));
        const desfaseResto = pad(Math.abs(desfaseMinutos) % 60);

        return `${año}-${mes}-${dia}T${hora}:${minuto}:${segundo}${signo}${desfaseHoras}:${desfaseResto}`;
    }

    function actualizarTemporizador(referenciaMs = Date.now()) {
        if (!inicioTimestamp) return;

        const diferencia = Math.max(
            0,
            Math.floor((referenciaMs - inicioTimestamp) / 1000)
        );
        const horas = Math.floor(diferencia / 3600);
        const minutos = Math.floor((diferencia % 3600) / 60);
        const segundos = diferencia % 60;

        const pad = (n) => String(n).padStart(2, '0');
        temporizador.textContent = `${pad(horas)}:${pad(minutos)}:${pad(segundos)}`;
    }

    function detenerTemporizador() {
        if (intervalo !== null) {
            clearInterval(intervalo);
            intervalo = null;
        }
    }

    // ---------------------------------------------------------
    // Almacenamiento en el navegador
    // (try/catch: en modo privado o con almacenamiento bloqueado
    // el cronómetro sigue funcionando, solo que sin protección)
    // ---------------------------------------------------------

    function guardarEstado(inicioMs, finalMs) {
        try {
            localStorage.setItem(
                CLAVE_CRONOMETRO,
                JSON.stringify({ inicio: inicioMs, final: finalMs })
            );
        } catch (error) {
            console.warn('No se pudo guardar el cronómetro:', error);
        }
    }

    function leerEstado() {
        try {
            const datos = JSON.parse(
                localStorage.getItem(CLAVE_CRONOMETRO)
            );

            if (!datos || !Number.isFinite(datos.inicio)) {
                return null;
            }

            if (
                datos.final !== null &&
                !(Number.isFinite(datos.final) && datos.final > datos.inicio)
            ) {
                return null;
            }

            return datos;
        } catch (error) {
            return null;
        }
    }

    function borrarEstado() {
        try {
            localStorage.removeItem(CLAVE_CRONOMETRO);
        } catch (error) {
            console.warn('No se pudo borrar el cronómetro:', error);
        }
    }

    // Horas que devolvió el servidor (error del formulario
    // o vuelta desde "Añadir nueva ubicación")
    function leerCamposOcultos() {
        if (!campoInicio.value) return null;

        const inicio = Date.parse(campoInicio.value);

        if (Number.isNaN(inicio)) return null;

        const final = campoFinal.value
            ? Date.parse(campoFinal.value)
            : null;

        if (
            final !== null &&
            (Number.isNaN(final) || final <= inicio)
        ) {
            return null;
        }

        return { inicio: inicio, final: final };
    }

    // ---------------------------------------------------------
    // Estados de la pantalla
    // ---------------------------------------------------------

    function mostrarSinIniciar() {
        detenerTemporizador();
        inicioTimestamp = null;

        campoInicio.value = '';
        campoFinal.value = '';
        horaInicio.textContent = '—';
        horaFinal.textContent = '—';
        temporizador.textContent = '00:00:00';
        estado.textContent = 'Sin iniciar';

        btnIniciar.disabled = false;
        btnTerminar.disabled = true;
        btnReiniciar.disabled = true;
        btnRegistrar.disabled = true;
    }

    function mostrarEnProgreso(inicio) {
        detenerTemporizador();
        inicioTimestamp = inicio.getTime();

        campoInicio.value = formatearFechaDjango(inicio);
        campoFinal.value = '';
        horaInicio.textContent = formatearHora(inicio);
        horaFinal.textContent = '—';
        estado.textContent = 'En progreso';

        btnIniciar.disabled = true;
        btnTerminar.disabled = false;
        btnReiniciar.disabled = false;
        btnRegistrar.disabled = true;

        intervalo = setInterval(actualizarTemporizador, 250);
        actualizarTemporizador();
    }

    function mostrarFinalizada(inicio, final) {
        detenerTemporizador();
        inicioTimestamp = inicio.getTime();

        campoInicio.value = formatearFechaDjango(inicio);
        campoFinal.value = formatearFechaDjango(final);
        horaInicio.textContent = formatearHora(inicio);
        horaFinal.textContent = formatearHora(final);
        actualizarTemporizador(final.getTime());
        estado.textContent = 'Finalizada';

        btnIniciar.disabled = true;
        btnTerminar.disabled = true;
        btnReiniciar.disabled = false;
        btnRegistrar.disabled = false;
    }

    function aplicarEstado(datos) {
        const inicio = new Date(datos.inicio);

        if (datos.final === null) {
            mostrarEnProgreso(inicio);
        } else {
            mostrarFinalizada(inicio, new Date(datos.final));
        }
    }

    // ---------------------------------------------------------
    // Botones
    // ---------------------------------------------------------

    btnIniciar.addEventListener('click', function () {
        const ahora = new Date();

        mostrarEnProgreso(ahora);
        guardarEstado(ahora.getTime(), null);
    });

    btnTerminar.addEventListener('click', function () {
        if (!inicioTimestamp) return;

        const ahora = new Date();

        mostrarFinalizada(new Date(inicioTimestamp), ahora);
        guardarEstado(inicioTimestamp, ahora.getTime());
    });

    btnReiniciar.addEventListener('click', function () {
        const confirmar = confirm(
            '¿Seguro que quieres reiniciar la cagada? Se perderá el tiempo registrado actualmente.'
        );

        if (confirmar) {
            borrarEstado();
            mostrarSinIniciar();
        }
    });

    // Solo el botón "Registrar cagada" borra el estado guardado.
    // Si el servidor rechaza el formulario, la página vuelve con
    // las horas en los campos ocultos y se recuperan de ahí.
    formulario.addEventListener('submit', function (evento) {
        if (evento.submitter === btnRegistrar) {
            borrarEstado();
        }
    });

    // Al volver con el botón "Atrás" el navegador puede mostrar la
    // página guardada en memoria: se sincroniza con lo almacenado
    // (evita registrar dos veces la misma cagada)
    window.addEventListener('pageshow', function (evento) {
        if (!evento.persisted) return;

        const datos = leerEstado();

        if (datos) {
            aplicarEstado(datos);
        } else {
            mostrarSinIniciar();
        }
    });

    // ---------------------------------------------------------
    // Al cargar la página: campos ocultos > almacenamiento > vacío
    // ---------------------------------------------------------

    const datosIniciales = leerCamposOcultos() || leerEstado();

    if (datosIniciales) {
        aplicarEstado(datosIniciales);
        guardarEstado(datosIniciales.inicio, datosIniciales.final);
    } else {
        mostrarSinIniciar();
    }
});

document.addEventListener('DOMContentLoaded', () => {

    const botonesReaccion = document.querySelectorAll(
        '.boton-reaccion'
    );

    botonesReaccion.forEach((boton) => {

        boton.addEventListener('click', async () => {

            const url = boton.dataset.url;
            const contenedor = boton.closest('.reacciones');

            try {

                const respuesta = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': obtenerCSRFToken()
                    }
                });

                if (!respuesta.ok) {
                    throw new Error(
                        'No se pudo registrar la reacción.'
                    );
                }

                const datos = await respuesta.json();

                actualizarReacciones(
                    contenedor,
                    datos.reacciones
                );

            } catch (error) {

                console.error(
                    'Error al reaccionar:',
                    error
                );

            }

        });

    });

});


function obtenerCSRFToken() {

    const cookies = document.cookie.split(';');

    for (const cookie of cookies) {

        const [nombre, valor] = cookie.trim().split('=');

        if (nombre === 'csrftoken') {
            return decodeURIComponent(valor);
        }

    }

    return '';
}


function actualizarReacciones(
    contenedor,
    reacciones
) {

    const botones = contenedor.querySelectorAll(
        '.boton-reaccion'
    );

    botones.forEach((boton) => {

        const tipo = boton.dataset.tipo;

        const contador = boton.querySelector(
            '.contador-reaccion'
        );

        contador.textContent = reacciones[tipo] ?? 0;

    });

}



// =========================================================
// VALIDACIÓN EN TIEMPO REAL DE LA CALIFICACIÓN (registrar)
// =========================================================

document.addEventListener('DOMContentLoaded', () => {

    // Solo el input numérico del registro: el feed también carga este
    // archivo y tiene un <select> con el mismo id en sus filtros
    const campoCalificacion = document.querySelector(
        'input[type="number"]#id_calificacion'
    );

    if (!campoCalificacion) {
        return;
    }

    const avisoCalificacion = document.createElement('span');

    avisoCalificacion.id = 'aviso-calificacion';
    avisoCalificacion.setAttribute('aria-live', 'polite');
    avisoCalificacion.style.color = 'red';
    avisoCalificacion.style.marginLeft = '0.5rem';

    campoCalificacion.insertAdjacentElement(
        'afterend',
        avisoCalificacion
    );

    function obtenerMensajeCalificacion() {

        // El navegador marca badInput si lo escrito no es un número
        if (campoCalificacion.validity.badInput) {
            return 'Solo se admiten números, por ejemplo 4.5.';
        }

        const valor = campoCalificacion.value.trim();

        if (valor === '') {
            return 'La calificación es obligatoria.';
        }

        if (!/^\d+(\.\d+)?$/.test(valor)) {
            return 'Solo se admiten números positivos, por ejemplo 4.5.';
        }

        const numero = Number(valor);

        if (numero < 0 || numero > 5) {
            return 'La calificación debe estar entre 0 y 5.';
        }

        if (!/^\d+(\.\d)?$/.test(valor)) {
            return 'Usa como máximo un decimal, por ejemplo 4.5.';
        }

        return '';
    }

    function validarCalificacion() {

        const mensaje = obtenerMensajeCalificacion();

        // Con un mensaje no vacío, el navegador bloquea el envío del formulario
        campoCalificacion.setCustomValidity(mensaje);

        campoCalificacion.setAttribute(
            'aria-invalid',
            mensaje ? 'true' : 'false'
        );

        avisoCalificacion.textContent = mensaje;
    }

    campoCalificacion.addEventListener('input', validarCalificacion);
    campoCalificacion.addEventListener('blur', validarCalificacion);

    // Si la página volvió del servidor con un valor, validarlo de una vez
    if (campoCalificacion.value !== '') {
        validarCalificacion();
    }

});