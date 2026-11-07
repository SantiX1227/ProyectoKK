console.log('cagadas.js cargado');
document.addEventListener('DOMContentLoaded', function () {
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

    let inicioTimestamp = null;
    let intervalo = null;

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

        const diferencia = Math.floor((referenciaMs - inicioTimestamp) / 1000);
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

    function reiniciarEstado() {
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

    btnIniciar.addEventListener('click', function () {
        const ahora = new Date();
        inicioTimestamp = ahora.getTime();

        campoInicio.value = formatearFechaDjango(ahora);
        campoFinal.value = '';
        horaInicio.textContent = formatearHora(ahora);
        horaFinal.textContent = '—';
        temporizador.textContent = '00:00:00';
        estado.textContent = 'En progreso';

        btnIniciar.disabled = true;
        btnTerminar.disabled = false;
        btnReiniciar.disabled = false;
        btnRegistrar.disabled = true;

        intervalo = setInterval(actualizarTemporizador, 250);
        actualizarTemporizador();
    });

    btnTerminar.addEventListener('click', function () {
        if (!inicioTimestamp) return;

        const ahora = new Date();
        detenerTemporizador();

        campoFinal.value = formatearFechaDjango(ahora);
        horaFinal.textContent = formatearHora(ahora);
        actualizarTemporizador(ahora.getTime());

        estado.textContent = 'Finalizada';
        btnTerminar.disabled = true;
        btnReiniciar.disabled = false;
        btnRegistrar.disabled = false;
    });

    btnReiniciar.addEventListener('click', function () {
        const confirmar = confirm(
            '¿Seguro que quieres reiniciar la cagada? Se perderá el tiempo registrado actualmente.'
        );

        if (confirmar) {
            reiniciarEstado();
        }
    });
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