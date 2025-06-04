document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('.btn-formacion').forEach(button => {
        button.addEventListener('click', async () => {
            // Obtiene el valor de la formación seleccionada desde el atributo data-formacion
            const formacion = button.dataset.formacion;

            // ACTUALIZA el input oculto del formulario con la formación seleccionada
            document.getElementById('formacion-input').value = formacion;

            try {
                const response = await fetch(`?formacion=${formacion}`);
                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const nuevaCancha = doc.querySelector('.cancha');

                // Reemplaza el contenido actual de la cancha por el nuevo
                document.querySelector('.cancha').replaceWith(nuevaCancha);

            } catch (error) {
                console.error('Error al actualizar la formación:', error);
            }
        });
    });
});
