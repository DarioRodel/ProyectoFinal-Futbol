document.addEventListener('DOMContentLoaded', function() {
    // Configuraciones de posición para cada formación
    const formacionesConfig = {
        '4-4-2': {
            descripcion: "Clásica formación balanceada",
            posiciones: [
                { top: '85%', left: '50%', rol: 'Portero' },
                { top: '65%', left: '20%', rol: 'Defensa' },
                { top: '65%', left: '35%', rol: 'Defensa' },
                { top: '65%', left: '65%', rol: 'Defensa' },
                { top: '65%', left: '80%', rol: 'Defensa' },
                { top: '45%', left: '15%', rol: 'Mediocampista' },
                { top: '45%', left: '35%', rol: 'Mediocampista' },
                { top: '45%', left: '65%', rol: 'Mediocampista' },
                { top: '45%', left: '85%', rol: 'Mediocampista' },
                { top: '25%', left: '35%', rol: 'Delantero' },
                { top: '25%', left: '65%', rol: 'Delantero' }
            ]
        },
        '4-3-3': {
            descripcion: "Formación ofensiva con tres delanteros",
            posiciones: [
                // ... configura posiciones similares para 4-3-3
            ]
        },
        '3-5-2': {
            descripcion: "Formación con énfasis en el mediocampo",
            posiciones: [
                // ... configura posiciones similares para 3-5-2
            ]
        },
        '4-2-3-1': {
            descripcion: "Formación moderna con mediocampista ofensivo",
            posiciones: [
                // ... configura posiciones similares para 4-2-3-1
            ]
        }
    };

    // Elementos del DOM
    const formacionBtns = document.querySelectorAll('.formacion-btn');
    const formacionInput = document.getElementById('formacion-input');
    const formacionPreview = document.getElementById('formacion-preview');
    const cancha = document.getElementById('cancha');
    const jugadoresCards = document.querySelectorAll('.jugador-card');

    // Inicializar con la formación actual
    const formacionActual = formacionInput.value;
    actualizarFormacion(formacionActual);

    // Event listeners para botones de formación
    formacionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const nuevaFormacion = this.dataset.formacion;
            formacionInput.value = nuevaFormacion;
            actualizarFormacion(nuevaFormacion);

            // Actualizar estado activo de los botones
            formacionBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Función para actualizar la vista de la formación
    function actualizarFormacion(formacion) {
        formacionPreview.innerHTML = '';
        formacionPreview.dataset.formacion = formacion;

        const config = formacionesConfig[formacion];

        config.posiciones.forEach((pos, index) => {
            const posicionElement = document.createElement('div');
            posicionElement.className = 'posicion-jugador';
            posicionElement.style.top = pos.top;
            posicionElement.style.left = pos.left;
            posicionElement.dataset.posicion = index + 1;
            posicionElement.dataset.rol = pos.rol;
            posicionElement.textContent = index + 1;
            posicionElement.title = `${pos.rol} - Posición ${index + 1}`;

            formacionPreview.appendChild(posicionElement);
        });
    }

    // Implementación básica de drag and drop
    jugadoresCards.forEach(jugador => {
        jugador.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', this.dataset.id);
            setTimeout(() => this.classList.add('dragging'), 0);
        });

        jugador.addEventListener('dragend', function() {
            this.classList.remove('dragging');
        });
    });

    cancha.addEventListener('dragover', function(e) {
        e.preventDefault();
    });

    cancha.addEventListener('drop', function(e) {
        e.preventDefault();
        const jugadorId = e.dataTransfer.getData('text/plain');
        const jugadorCard = document.querySelector(`.jugador-card[data-id="${jugadorId}"]`);
        const posicionJugador = e.target.closest('.posicion-jugador');

        if (posicionJugador) {
            // Aquí puedes implementar la lógica para asignar el jugador a la posición
            console.log(`Asignar jugador ${jugadorId} a posición ${posicionJugador.dataset.posicion}`);
            posicionJugador.textContent = jugadorCard.textContent;
            posicionJugador.style.backgroundColor = 'rgba(255, 193, 7, 0.7)';
        }
    });
});