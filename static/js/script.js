document.getElementById('addPersonalForm')?.addEventListener('submit', function(e) {
    const nameInput = document.getElementById('name');
    const cargoSelect = document.getElementById('cargo');

    if (!nameInput.value || cargoSelect.value === '') {
        e.preventDefault();
        alert('Por favor, completa todos los campos antes de agregar.');
    } else {
        alert('Personal agregado correctamente. Selecciona para ingresar.');
    }
});

document.getElementById('uploadForm')?.addEventListener('submit', function(e) {
    const fileInput = document.getElementById('file');

    if (!fileInput.value) {
        e.preventDefault();
        alert('Por favor, selecciona un archivo antes de enviar.');
    } else {
        alert('Procesando tu CV, por favor espera...');
    }
});

document.getElementById('cargo')?.addEventListener('change', function() {
    this.style.borderColor = '#4682B4';
});