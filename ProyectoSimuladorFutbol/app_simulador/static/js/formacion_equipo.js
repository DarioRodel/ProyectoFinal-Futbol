document.addEventListener('DOMContentLoaded', function() {
    // Event listeners para los botones de formación
    document.querySelectorAll('.btn-formacion').forEach(btn => {
        btn.addEventListener('click', function() {
            const formacion = this.dataset.formacion;
            document.getElementById('formacion-input').value = formacion;

            // Actualizar la clase activa
            document.querySelectorAll('.btn-formacion').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Actualizar la clase de formación en la cancha
            const cancha = document.querySelector('.cancha');
            cancha.className = 'cancha formacion-' + formacion;
        });
    });
});
