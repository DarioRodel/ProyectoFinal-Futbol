document.addEventListener('DOMContentLoaded', function() {
    // Obtener la formación actual
    const formacionActual = document.getElementById('formacion-input').value || '4-4-2';
    
    // Generar los puntos según la formación
    generarPuntosFormacion(formacionActual);
    
    // Event listeners para los botones de formación
    document.querySelectorAll('.btn-formacion').forEach(btn => {
        btn.addEventListener('click', function() {
            const formacion = this.dataset.formacion;
            document.getElementById('formacion-input').value = formacion;
            
            // Actualizar la vista previa
            const preview = document.getElementById('formacion-preview');
            preview.className = `formacion-${formacion}`;
            
            // Regenerar los puntos
            preview.innerHTML = '';
            generarPuntosFormacion(formacion);
            
            // Actualizar clase activa
            document.querySelectorAll('.btn-formacion').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

function generarPuntosFormacion(formacion) {
    const preview = document.getElementById('formacion-preview');
    
    // Mapeo de formaciones a puntos
    const formaciones = {
        '4-4-2': {
            porteros: 1,
            defensas: 4,
            mediocampistas: 4,
            delanteros: 2
        },
        '4-3-3': {
            porteros: 1,
            defensas: 4,
            mediocampistas: 3,
            delanteros: 3
        },
        '3-5-2': {
            porteros: 1,
            defensas: 3,
            mediocampistas: 5,
            delanteros: 2
        },
        '4-2-3-1': {
            porteros: 1,
            defensas: 4,
            mediocampistasDefensivos: 2,
            mediocampistasOfensivos: 3,
            delanteros: 1
        }
    };
    
    const config = formaciones[formacion];
    let numeroJugador = 1;
    
    // Portero (siempre 1)
    const portero = document.createElement('div');
    portero.className = 'punto-alineacion punto-portero';
    portero.textContent = numeroJugador++;
    preview.appendChild(portero);
    
    // Defensas
    for (let i = 1; i <= config.defensas; i++) {
        const defensa = document.createElement('div');
        defensa.className = `punto-alineacion punto-defensa punto-defensa-${i}`;
        defensa.textContent = numeroJugador++;
        preview.appendChild(defensa);
    }
    
    // Mediocampistas
    if (formacion === '4-2-3-1') {
        // Caso especial para 4-2-3-1
        for (let i = 1; i <= config.mediocampistasDefensivos; i++) {
            const medio = document.createElement('div');
            medio.className = `punto-alineacion punto-mediocampista-defensivo punto-mediocampista-defensivo-${i}`;
            medio.textContent = numeroJugador++;
            preview.appendChild(medio);
        }
        
        for (let i = 1; i <= config.mediocampistasOfensivos; i++) {
            const medio = document.createElement('div');
            medio.className = `punto-alineacion punto-mediocampista-ofensivo punto-mediocampista-ofensivo-${i}`;
            medio.textContent = numeroJugador++;
            preview.appendChild(medio);
        }
    } else {
        // Otras formaciones
        for (let i = 1; i <= config.mediocampistas; i++) {
            const medio = document.createElement('div');
            medio.className = `punto-alineacion punto-mediocampista punto-mediocampista-${i}`;
            medio.textContent = numeroJugador++;
            preview.appendChild(medio);
        }
    }
    
    // Delanteros
    for (let i = 1; i <= config.delanteros; i++) {
        const delantero = document.createElement('div');
        delantero.className = `punto-alineacion punto-delantero punto-delantero-${i}`;
        delantero.textContent = numeroJugador++;
        preview.appendChild(delantero);
    }
}