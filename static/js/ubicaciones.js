document.addEventListener('DOMContentLoaded', () => {

    const campoLatitud = document.getElementById('id_latitud');
    const campoLongitud = document.getElementById('id_longitud');
    const botonGeolocalizar = document.getElementById('btn-geolocalizar');
    const estadoGeolocalizacion = document.getElementById('estado-geolocalizacion');

    if (
        !campoLatitud ||
        !campoLongitud ||
        !botonGeolocalizar ||
        !estadoGeolocalizacion
    ) {
        return;
    }

    // La geolocalización solo funciona en contexto seguro (HTTPS o localhost)
    if (!('geolocation' in navigator) || !window.isSecureContext) {

        botonGeolocalizar.disabled = true;

        estadoGeolocalizacion.textContent =
            'Tu navegador no permite obtener la ubicación en esta página. ' +
            'Escribe las coordenadas a mano.';

        return;
    }

    const mensajesError = {
        1: 'Permiso denegado. Puedes escribir las coordenadas a mano ' +
           'o permitir la ubicación en el navegador y volver a intentarlo.',
        2: 'No se pudo determinar tu ubicación. Escribe las coordenadas a mano.',
        3: 'La ubicación tardó demasiado en responder. Vuelve a intentarlo.',
    };

    function obtenerUbicacion() {

        botonGeolocalizar.disabled = true;

        estadoGeolocalizacion.textContent = 'Obteniendo tu ubicación…';

        navigator.geolocation.getCurrentPosition(

            (posicion) => {

                // 6 decimales: lo que admite el modelo (decimal_places=6)
                campoLatitud.value = posicion.coords.latitude.toFixed(6);
                campoLongitud.value = posicion.coords.longitude.toFixed(6);

                const precision = Math.round(posicion.coords.accuracy);

                estadoGeolocalizacion.textContent =
                    `Ubicación capturada (precisión aproximada: ${precision} m). ` +
                    'Puedes ajustarla si hace falta.';

                botonGeolocalizar.disabled = false;
            },

            (error) => {

                estadoGeolocalizacion.textContent =
                    mensajesError[error.code] ||
                    'No se pudo obtener la ubicación.';

                botonGeolocalizar.disabled = false;
            },

            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000,
            }
        );
    }

    botonGeolocalizar.addEventListener('click', obtenerUbicacion);

    // Captura automática solo si la página lo permite (no en editar)
    // y si los campos están vacíos (no pisa lo que ya escribió el usuario)
    const capturaAutomatica =
        botonGeolocalizar.dataset.automatica !== 'false';

    if (
        capturaAutomatica &&
        !campoLatitud.value &&
        !campoLongitud.value
    ) {
        obtenerUbicacion();
    }

});