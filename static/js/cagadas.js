document.addEventListener('DOMContentLoaded', function () {
    const btnIniciar = document.getElementById('btn-iniciar');
    const btnTerminar = document.getElementById('btn-terminar');
    const btnRegistrar = document.getElementById('btn-registrar');
    const estado = document.getElementById('estado');
    const horaInicio = document.getElementById('hora-inicio');
    const horaFinal = document.getElementById('hora-final');
    const temporizador = document.getElementById('temporizador');
    const campoInicio = document.getElementById('id_hora_inicio_cagada');
    const campoFinal = document.getElementById('id_hora_final_cagada');

    if (!btnIniciar || !btnTerminar || !btnRegistrar || !estado || !horaInicio || !horaFinal || !temporizador || !campoInicio || !campoFinal) {
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

        return `${año}-${mes}-${dia}T${hora}:${minuto}:${segundo}`;
    }

    function actualizarTemporizador() {
        if (!inicioTimestamp) return;

        const diferencia = Math.floor((Date.now() - inicioTimestamp) / 1000);
        const horas = Math.floor(diferencia / 3600);
        const minutos = Math.floor((diferencia % 3600) / 60);
        const segundos = diferencia % 60;

        const pad = (n) => String(n).padStart(2, '0');
        temporizador.textContent = `${pad(horas)}:${pad(minutos)}:${pad(segundos)}`;
    }

    btnIniciar.addEventListener('click', function () {
        const ahora = new Date();
        inicioTimestamp = ahora.getTime();

        campoInicio.value = formatearFechaDjango(ahora);
        horaInicio.textContent = formatearHora(ahora);
        estado.textContent = 'En progreso';

        btnIniciar.disabled = true;
        btnTerminar.disabled = false;
        btnRegistrar.disabled = true;

        intervalo = setInterval(actualizarTemporizador, 250);
        actualizarTemporizador();
    });

    btnTerminar.addEventListener('click', function () {
        if (!inicioTimestamp) return;

        const ahora = new Date();
        campoFinal.value = formatearFechaDjango(ahora);
        horaFinal.textContent = formatearHora(ahora);

        actualizarTemporizador();
        estado.textContent = 'Finalizada';

        btnTerminar.disabled = true;
        btnRegistrar.disabled = false;

        clearInterval(intervalo);
    });
});