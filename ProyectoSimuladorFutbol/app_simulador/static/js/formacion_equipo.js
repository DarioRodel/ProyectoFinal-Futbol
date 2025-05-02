// Espera a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {

    // Selecciona todos los botones que permiten elegir una formación
    document.querySelectorAll('.btn-formacion').forEach(button => {

        // Añade un listener de clic a cada botón
        button.addEventListener('click', async () => {
            // Obtiene el valor de la formación seleccionada desde el atributo data-formacion
            const formacion = button.dataset.formacion;

            // ACTUALIZA el input oculto del formulario con la formación seleccionada
            document.getElementById('formacion-input').value = formacion;

            try {
                // Hace una petición GET con la formación como parámetro
                const response = await fetch(`?formacion=${formacion}`);
                // Obtiene la respuesta como texto HTML
                const html = await response.text();

                // Usa DOMParser para convertir el HTML recibido en un documento
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');

                // Extrae el nuevo contenido de la cancha del HTML recibido
                const nuevaCancha = doc.querySelector('.cancha');

                // Reemplaza el contenido actual de la cancha por el nuevo
                document.querySelector('.cancha').replaceWith(nuevaCancha);

            } catch (error) {
                // Si algo sale mal, muestra un error en la consola
                console.error('Error al actualizar la formación:', error);
            }
        });
    });
});
