// static/js/analytics.js
// Fase E: lleva a la comparación con el usuario elegido.
// Si no se eligió ninguno, muestra un aviso en la página (sin alert()).

document.addEventListener('DOMContentLoaded', () => {

    const formulario = document.getElementById('form-comparacion');

    if (!formulario) {
        return;
    }

    const selector = document.getElementById('usuario-comparacion');
    const aviso = document.getElementById('aviso-comparacion');

    formulario.addEventListener('submit', (evento) => {

        evento.preventDefault();

        if (!selector.value) {
            aviso.hidden = false;
            selector.focus();
            return;
        }

        window.location.href = selector.value;
    });

    // En cuanto elige a alguien, el aviso sobra
    selector.addEventListener('change', () => {
        aviso.hidden = true;
    });

});
