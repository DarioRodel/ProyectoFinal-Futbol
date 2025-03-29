// Función para actualizar la formación visible
function actualizarFormacion(formacion) {
    const formacionPreview = document.getElementById('formacion-preview');
    formacionPreview.className = `formacion-${formacion}`;

    // Ocultar todos los puntos primero
    const puntos = document.querySelectorAll('.punto-alineacion');
    puntos.forEach(punto => punto.style.display = 'none');

    // Mostrar solo los puntos necesarios para esta formación
    let puntosAMostrar = [];

    if (formacion === '4-4-2') {
        puntosAMostrar = ['portero', 'defensa-1', 'defensa-2', 'defensa-3', 'defensa-4',
                         'mediocampista-1', 'mediocampista-2', 'mediocampista-3', 'mediocampista-4',
                         'delantero-1', 'delantero-2'];
    } else if (formacion === '4-3-3') {
        puntosAMostrar = ['portero', 'defensa-1', 'defensa-2', 'defensa-3', 'defensa-4',
                         'mediocampista-1', 'mediocampista-2', 'mediocampista-3',
                         'delantero-1', 'delantero-2', 'delantero-3'];
    } else if (formacion === '3-5-2') {
        puntosAMostrar = ['portero', 'defensa-1', 'defensa-2', 'defensa-3',
                         'mediocampista-1', 'mediocampista-2', 'mediocampista-3', 'mediocampista-4', 'mediocampista-5',
                         'delantero-1', 'delantero-2'];
    } else if (formacion === '4-2-3-1') {
        puntosAMostrar = ['portero', 'defensa-1', 'defensa-2', 'defensa-3', 'defensa-4',
                         'mediocampista-defensivo-1', 'mediocampista-defensivo-2',
                         'mediocampista-ofensivo-1', 'mediocampista-ofensivo-2', 'mediocampista-ofensivo-3',
                         'delantero'];
    }

    puntosAMostrar.forEach(punto => {
        document.querySelector(`.punto-${punto}`).style.display = 'flex';
    });
}

// Manejar selección de formación
const formacionBtns = document.querySelectorAll('.btn-formacion');
const formacionInput = document.getElementById('formacion-input');

formacionBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        formacionBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');

        const formacion = this.dataset.formacion;
        formacionInput.value = formacion;
        actualizarFormacion(formacion);
    });
});

// Inicializar con la formación actual
const formacionActual = formacionInput.value || '4-4-2';
document.querySelector(`.btn-formacion[data-formacion="${formacionActual}"]`).classList.add('active');
actualizarFormacion(formacionActual);