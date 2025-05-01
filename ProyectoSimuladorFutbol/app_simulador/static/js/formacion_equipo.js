document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-formacion').forEach(button => {
        button.addEventListener('click', async () => {
            const formacion = button.dataset.formacion;

            // ACTUALIZA el input oculto del formulario
            document.getElementById('formacion-input').value = formacion;

            // AJAX: Carga dinámica de la cancha
            try {
                const response = await fetch(`?formacion=${formacion}`);
                const html = await response.text();

                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const nuevaCancha = doc.querySelector('.cancha');
                document.querySelector('.cancha').replaceWith(nuevaCancha);

            } catch (error) {
                console.error('Error al actualizar la formación:', error);
            }
        });
    });
});
