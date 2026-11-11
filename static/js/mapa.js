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

    // Con ratón, la rueda solo hace zoom cuando ya estás usando el mapa
    // (clic, empezar a arrastrar o llegar con el teclado). Así, al bajar
    // por la página con la rueda, el mapa no "atrapa" el desplazamiento.
    // Al sacar el ratón del mapa se vuelve a desactivar.
    mapa.on('mousedown focus', function () {
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

    // Encuadre primero: Leaflet no crea los iconos de los marcadores
    // hasta que el mapa tiene una vista (y abajo se usan sus elementos).
    // Con una sola ubicación, zoom de calle; con varias, que se vean todas.
    const posiciones = ubicaciones.map(function (lugar) {
        return [lugar.latitud, lugar.longitud];
    });

    if (posiciones.length === 1) {
        mapa.setView(posiciones[0], 16);
    } else {
        mapa.fitBounds(posiciones, {
            padding: [40, 40],
            maxZoom: 17
        });
    }

    // Centro de gravedad y radio de acción (paso 6). Van fuera del
    // grupo de pines para que nunca se agrupen con ellos.
    const datosCentro = document.getElementById('centro-mapa');

    if (datosCentro) {
        agregarCentro(mapa, JSON.parse(datosCentro.textContent));
    }

    // Agrupa los pines que quedan muy cerca (p. ej. dos baños de la
    // misma casa). Al tocar un grupo se acerca el zoom; si aun así los
    // lugares coinciden, se abren en abanico ("spiderfy").
    const grupo = L.markerClusterGroup({
        maxClusterRadius: 40,
        showCoverageOnHover: false,
        spiderfyOnMaxZoom: true,
        spiderLegPolylineOptions: {
            color: '#7b6b5e',
            weight: 1.5,
            opacity: 0.7
        },
        iconCreateFunction: crearGrupo
    });

    ubicaciones.forEach(function (lugar, indice) {
        const marcador = L.marker(posiciones[indice], {
            icon: crearPin(lugar),
            keyboard: true,
            title: lugar.nombre,
            // Los lugares más usados quedan por encima si se solapan
            zIndexOffset: lugar.nivel * 100 + (lugar.favorita ? 1000 : 0),
            // Lo usa crearGrupo para colorear el grupo
            nivel: lugar.nivel
        })
            .bindPopup(function () {
                return crearPopup(lugar);
            });

        // Nombre accesible para lectores de pantalla y teclado.
        // Dentro de un grupo el pin no existe en la página hasta que
        // el grupo se abre, por eso se pone cada vez que aparece.
        marcador.on('add', function () {
            marcador.getElement().setAttribute(
                'aria-label',
                lugar.nombre + ': ' + lugar.cantidad +
                    (lugar.cantidad === 1 ? ' cagada' : ' cagadas')
            );
        });

        // El pin con la ventana abierta se resalta
        marcador.on('popupopen', function () {
            marcador.getElement().classList.add('is-activo');
        });

        marcador.on('popupclose', function () {
            marcador.getElement().classList.remove('is-activo');
        });

        grupo.addLayer(marcador);
    });

    mapa.addLayer(grupo);
});

// ---------------------------------------------------------
// Pin de color según el nivel (colores en mapa.css).
// Solo lleva números: el nombre nunca entra en este HTML.
// ---------------------------------------------------------

function crearPin(lugar) {
    const numero = lugar.cantidad > 99 ? '99+' : String(lugar.cantidad);

    let clases = 'pin nivel-' + Number(lugar.nivel);

    if (lugar.favorita) {
        clases += ' es-favorita';
    }

    return L.divIcon({
        className: clases,
        html: '<span class="pin-forma"><span class="pin-numero">' + numero + '</span></span>',
        iconSize: [36, 46],
        iconAnchor: [18, 44],
        popupAnchor: [0, -40]
    });
}

// ---------------------------------------------------------
// Centro de gravedad: el punto medio de tus cagadas (contando
// más los lugares más usados) y un círculo discontinuo con el
// radio de acción (hasta el lugar usado más lejano).
// ---------------------------------------------------------

function agregarCentro(mapa, centro) {
    const posicion = [centro.latitud, centro.longitud];

    // Con un radio muy pequeño el círculo no aporta nada
    if (centro.radio_metros >= 30) {
        L.circle(posicion, {
            radius: centro.radio_metros,
            color: '#b5541c',
            weight: 1.5,
            dashArray: '6 6',
            fillColor: '#b5541c',
            fillOpacity: 0.05,
            interactive: false
        }).addTo(mapa);
    }

    const marcador = L.marker(posicion, {
        icon: L.divIcon({
            className: 'centro',
            html: '<span class="centro-forma" aria-hidden="true">🎯</span>',
            iconSize: [30, 30]
        }),
        keyboard: true,
        title: 'Tu centro de gravedad',
        // Siempre por debajo de los pines
        zIndexOffset: -1000
    })
        .bindPopup(function () {
            return crearPopupCentro(centro);
        })
        .addTo(mapa);

    marcador.getElement().setAttribute('aria-label', 'Tu centro de gravedad');
}

function crearPopupCentro(centro) {
    const caja = crearElemento('div', 'popup-lugar popup-centro');

    caja.append(
        crearElemento('h3', 'popup-nombre', '🎯 Tu centro de gravedad')
    );

    caja.append(
        crearElemento(
            'p',
            null,
            'El punto medio de tus cagadas: cuenta más los lugares que más usas.'
        )
    );

    if (centro.radio_metros >= 30) {
        const radio = crearElemento('p', null, 'El círculo es tu radio de acción: ');
        radio.append(crearElemento('strong', null, centro.radio_texto));
        radio.append(' hasta el lugar más lejano donde has cagado.');

        caja.append(radio);
    }

    return caja;
}


// ---------------------------------------------------------
// Grupo de pines cercanos: círculo con el número de lugares,
// con el aro del color del nivel más alto que contiene.
// ---------------------------------------------------------

function crearGrupo(grupo) {
    const marcadores = grupo.getAllChildMarkers();

    const nivelMaximo = Math.max.apply(null, marcadores.map(function (marcador) {
        return Number(marcador.options.nivel) || 0;
    }));

    return L.divIcon({
        className: 'grupo nivel-' + nivelMaximo,
        html: '<span class="grupo-circulo"><strong>' + marcadores.length +
            '</strong><small>lugares</small></span>',
        iconSize: [48, 48]
    });
}



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