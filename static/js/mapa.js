// =========================================================
// MAPA DE UBICACIONES (privado)
// Lee los datos que deja la vista en #datos-mapa (json_script)
// y pinta un marcador por ubicación con una ventana de datos.
// Si Leaflet no carga (sin conexión), se queda el aviso
// provisional de la plantilla.
// =========================================================

document.addEventListener('DOMContentLoaded', function () {
    const contenedor = document.getElementById('mapa');
    const datos = document.getElementById('datos-mapa');

    if (!contenedor || !datos || typeof L === 'undefined') {
        return;
    }

    const ubicaciones = JSON.parse(datos.textContent);

    if (!ubicaciones.length) {
        return;
    }

    contenedor.classList.remove('mapa-provisional');
    contenedor.replaceChildren();

    const mapa = L.map(contenedor, {
        scrollWheelZoom: false
    });

    // Con ratón, la rueda solo hace zoom después de hacer clic en el
    // mapa (así no "atrapa" el desplazamiento de la página)
    mapa.on('click', function () {
        mapa.scrollWheelZoom.enable();
    });

    mapa.on('mouseout', function () {
        mapa.scrollWheelZoom.disable();
    });

    // OpenStreetMap exige saber desde qué sitio se piden los mosaicos.
    // Django envía "Referrer-Policy: same-origin" (no manda el Referer
    // a otros dominios), así que solo para los mosaicos se envía el
    // origen (p. ej. http://localhost:8000), nunca la ruta de la página.
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        referrerPolicy: 'strict-origin-when-cross-origin',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mapa);

    const posiciones = [];

    ubicaciones.forEach(function (lugar) {
        const posicion = [lugar.latitud, lugar.longitud];

        L.marker(posicion, {
            alt: lugar.nombre,
            keyboard: true
        })
            .bindPopup(function () {
                return crearPopup(lugar);
            })
            .addTo(mapa);

        posiciones.push(posicion);
    });

    // Encuadre: con una sola ubicación, zoom de calle;
    // con varias, que se vean todas
    if (posiciones.length === 1) {
        mapa.setView(posiciones[0], 16);
    } else {
        mapa.fitBounds(posiciones, {
            padding: [40, 40],
            maxZoom: 17
        });
    }
});


// ---------------------------------------------------------
// Ventana emergente. Se construye con nodos (textContent),
// nunca con innerHTML: el nombre y el tipo los escribe el
// usuario y podrían contener HTML.
// ---------------------------------------------------------

function crearPopup(lugar) {
    const caja = crearElemento('div', 'popup-lugar nivel-' + lugar.nivel);

    const cabecera = crearElemento('div', 'popup-cabecera');

    cabecera.append(
        crearElemento('h3', 'popup-nombre', (lugar.favorita ? '👑 ' : '') + lugar.nombre),
        crearElemento('span', 'popup-tipo', lugar.tipo)
    );

    const cifra = crearElemento('div', 'popup-cifra');

    cifra.append(
        crearElemento('strong', null, lugar.cantidad),
        crearElemento(
            'span',
            null,
            (lugar.cantidad === 1 ? 'cagada' : 'cagadas') +
                ' · ' + formatearNumero(lugar.porcentaje) + ' % del total'
        )
    );

    caja.append(cabecera, cifra);

    if (lugar.cantidad > 0) {
        const lista = crearElemento('dl', 'popup-datos');

        agregarDato(lista, 'Duración media', lugar.duracion_promedio || '—');

        agregarDato(
            lista,
            'Calificación',
            lugar.calificacion_promedio !== null
                ? '★ ' + formatearNumero(lugar.calificacion_promedio) + ' / 5'
                : '—'
        );

        agregarDato(lista, 'Última visita', lugar.ultima_visita || '—');

        caja.append(lista);
    } else {
        caja.append(
            crearElemento('p', 'popup-vacio', 'Todavía no has registrado cagadas aquí.')
        );
    }

    const enlace = crearElemento('a', 'popup-enlace', '✏️ Editar ubicación');
    enlace.href = lugar.url_editar;

    caja.append(enlace);

    return caja;
}

function crearElemento(etiqueta, clase, texto) {
    const nodo = document.createElement(etiqueta);

    if (clase) {
        nodo.className = clase;
    }

    if (texto !== undefined && texto !== null) {
        nodo.textContent = texto;
    }

    return nodo;
}

function agregarDato(lista, etiqueta, valor) {
    lista.append(
        crearElemento('dt', null, etiqueta),
        crearElemento('dd', null, valor)
    );
}

function formatearNumero(numero) {
    return Number(numero).toLocaleString('es-CO', {
        maximumFractionDigits: 1
    });
}