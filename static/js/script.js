// Variables globales
let editando = false;
let registroActual = null;

// Función para formatear la hora en formato de Perú
function formatearFecha(fechaString) {
    if (!fechaString) return '';
    const fecha = new Date(fechaString);
    
    // Ajustar para mostrar en formato dd/mm/yyyy HH:MM:SS
    const dia = String(fecha.getDate()).padStart(2, '0');
    const mes = String(fecha.getMonth() + 1).padStart(2, '0');
    const anio = fecha.getFullYear();
    const hora = String(fecha.getHours()).padStart(2, '0');
    const minutos = String(fecha.getMinutes()).padStart(2, '0');
    const segundos = String(fecha.getSeconds()).padStart(2, '0');
    
    return `${dia}/${mes}/${anio} ${hora}:${minutos}:${segundos}`;
}

// Actualizar la hora actual en tiempo real
function actualizarHora() {
    const ahora = new Date();
    
    // Convertir a zona horaria de Perú (UTC-5)
    const opciones = { 
        timeZone: 'America/Lima',
        day: '2-digit',
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    };
    
    const fechaFormateada = ahora.toLocaleString('es-PE', opciones);
    document.getElementById('currentDateTime').textContent = fechaFormateada;
}

// Función para mostrar el formulario
function mostrarFormulario() {
    document.getElementById('formularioRegistro').style.display = 'block';
    document.getElementById('historialRegistros').style.display = 'none';
    document.getElementById('pageTitleHeader').textContent = 'Registro de Movilidad';
    
    // Resetear el modo de edición
    if (!editando) {
        limpiarFormulario();
    }
}

// Función para mostrar el historial
function mostrarHistorial() {
    document.getElementById('formularioRegistro').style.display = 'none';
    document.getElementById('historialRegistros').style.display = 'block';
    document.getElementById('pageTitleHeader').textContent = 'Historial de Registros';
    
    // Cargar los registros
    cargarRegistros();
}

// Función para limpiar el formulario
function limpiarFormulario() {
    document.getElementById('registroForm').reset();
    document.getElementById('registroId').value = '';
    editando = false;
    registroActual = null;
    
    // Cambiar el texto del botón a "Guardar"
    const submitBtn = document.querySelector('#registroForm button[type="submit"]');
    submitBtn.textContent = 'Guardar';
}

// Función para cargar los registros en la tabla
function cargarRegistros() {
    fetch('/registros/')
        .then(response => response.json())
        .then(data => {
            const tablaBody = document.getElementById('tablaRegistros');
            tablaBody.innerHTML = '';
            
            if (data.length === 0) {
                tablaBody.innerHTML = '<tr><td colspan="10" class="text-center">No hay registros disponibles</td></tr>';
                return;
            }
            
            data.forEach(registro => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${registro.id}</td>
                    <td>${registro.nombre_chofer}</td>
                    <td><span class="badge ${registro.tipo === 'Entrada' ? 'bg-success' : 'bg-warning'}">${registro.tipo}</span></td>
                    <td>${registro.destino}</td>
                    <td>${registro.diligencia}</td>
                    <td>${registro.sustento}</td>
                    <td>${registro.solicitud}</td>
                    <td>${registro.responsable}</td>
                    <td>${formatearFecha(registro.fecha_hora)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary action-btn edit-btn" onclick="editarRegistro(${registro.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger action-btn delete-btn" onclick="confirmarEliminar(${registro.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tablaBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error al cargar los registros:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudieron cargar los registros. Intente nuevamente.',
            });
        });
}

// Función para recargar el historial
function recargarHistorial() {
    cargarRegistros();
    Swal.fire({
        icon: 'success',
        title: 'Actualizado',
        text: 'El historial ha sido actualizado',
        timer: 1500,
        showConfirmButton: false
    });
}

// Función para editar un registro
function editarRegistro(id) {
    fetch(`/registros/${id}`)
        .then(response => response.json())
        .then(data => {
            // Guardar referencia al registro actual
            registroActual = data;
            
            // Llenar el formulario con los datos
            document.getElementById('registroId').value = data.id;
            document.getElementById('nombre_chofer').value = data.nombre_chofer;
            document.getElementById('tipo').value = data.tipo;
            document.getElementById('destino').value = data.destino;
            document.getElementById('diligencia').value = data.diligencia;
            document.getElementById('sustento').value = data.sustento;
            document.getElementById('solicitud').value = data.solicitud;
            document.getElementById('responsable').value = data.responsable;
            
            // Cambiar a modo edición
            editando = true;
            
            // Cambiar el texto del botón a "Actualizar"
            const submitBtn = document.querySelector('#registroForm button[type="submit"]');
            submitBtn.textContent = 'Actualizar';
            
            // Mostrar el formulario
            mostrarFormulario();
            
            // Mostrar un mensaje
            Swal.fire({
                icon: 'info',
                title: 'Modo Edición',
                text: `Editando el registro #${data.id}`,
                timer: 2000,
                showConfirmButton: false
            });
        })
        .catch(error => {
            console.error('Error al obtener el registro:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudo cargar el registro para editar. Intente nuevamente.'
            });
        });
}

// Función para confirmar eliminación
function confirmarEliminar(id) {
    Swal.fire({
        icon: 'warning',
        title: '¿Está seguro?',
        text: `¿Desea eliminar el registro #${id}? Esta acción no se puede deshacer.`,
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#e74a3b',
        cancelButtonColor: '#3f51b5',
    }).then((result) => {
        if (result.isConfirmed) {
            eliminarRegistro(id);
        }
    });
}

// Función para eliminar un registro
function eliminarRegistro(id) {
    fetch(`/registros/${id}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        Swal.fire({
            icon: 'success',
            title: 'Eliminado',
            text: 'El registro ha sido eliminado exitosamente',
            timer: 1500,
            showConfirmButton: false
        });
        
        // Actualizar la tabla
        cargarRegistros();
    })
    .catch(error => {
        console.error('Error al eliminar el registro:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudo eliminar el registro. Intente nuevamente.'
        });
    });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Actualizar la hora cada segundo
    actualizarHora();
    setInterval(actualizarHora, 1000);
    
    // Listener para el formulario
    document.getElementById('registroForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Obtener los datos del formulario
        const id = document.getElementById('registroId').value;
        const formData = {
            nombre_chofer: document.getElementById('nombre_chofer').value,
            tipo: document.getElementById('tipo').value,
            destino: document.getElementById('destino').value,
            diligencia: document.getElementById('diligencia').value,
            sustento: document.getElementById('sustento').value,
            solicitud: document.getElementById('solicitud').value,
            responsable: document.getElementById('responsable').value
        };
        
        // Determinar si es creación o actualización
        if (editando && id) {
            // Actualizar registro existente
            fetch(`/registros/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                Swal.fire({
                    icon: 'success',
                    title: 'Actualizado',
                    text: 'El registro ha sido actualizado exitosamente',
                    timer: 1500,
                    showConfirmButton: false
                });
                
                // Limpiar formulario y mostrar historial
                limpiarFormulario();
                mostrarHistorial();
            })
            .catch(error => {
                console.error('Error al actualizar el registro:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo actualizar el registro. Intente nuevamente.'
                });
            });
        } else {
            // Crear nuevo registro
            fetch('/registros/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                Swal.fire({
                    icon: 'success',
                    title: 'Guardado',
                    text: 'El registro ha sido guardado exitosamente',
                    timer: 1500,
                    showConfirmButton: false
                });
                
                // Limpiar formulario y mostrar historial
                limpiarFormulario();
                mostrarHistorial();
            })
            .catch(error => {
                console.error('Error al crear el registro:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo crear el registro. Intente nuevamente.'
                });
            });
        }
    });
    
    // Mostrar el formulario por defecto
    mostrarFormulario();
});