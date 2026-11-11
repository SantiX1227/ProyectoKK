/* static/js/main.js
   JS global: se carga en todas las páginas desde base.html */

/* Modal de aviso (mensajes de Django).
   La plantilla lo pinta con "open" (visible aunque no haya JS);
   aquí se reabre con showModal() para que sea un modal real:
   fondo oscuro, foco atrapado y cierre con Esc. */
document.addEventListener('DOMContentLoaded', () => {

    const modal = document.getElementById('modal-aviso');

    if (!modal || typeof modal.showModal !== 'function') {
        return;
    }

    modal.close();
    modal.showModal();

    // Tocar fuera del recuadro (en el fondo) también lo cierra
    modal.addEventListener('click', (evento) => {

        if (evento.target === modal) {
            modal.close();
        }

    });

});