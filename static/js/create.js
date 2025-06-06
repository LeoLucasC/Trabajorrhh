document.addEventListener('DOMContentLoaded', function() {
    // Manejar navegación entre pasos
    const nextButtons = document.querySelectorAll('.clinica-button--next');
    const prevButtons = document.querySelectorAll('.clinica-button--prev');
    const steps = document.querySelectorAll('.clinica-form__step');
    const progressSteps = document.querySelectorAll('.clinica-form__progress-step');
    
    // Función para mostrar un paso específico
    function showStep(stepNumber) {
        steps.forEach((step, index) => {
            if (index + 1 === stepNumber) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        // Actualizar barra de progreso
        progressSteps.forEach((step, index) => {
            if (index + 1 <= stepNumber) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }
    
    // Event listeners para botones "Siguiente"
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const nextStep = parseInt(this.getAttribute('data-next'));
            showStep(nextStep);
        });
    });
    
    // Event listeners para botones "Anterior"
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            const prevStep = parseInt(this.getAttribute('data-prev'));
            showStep(prevStep);
        });
    });
    
    // Generar resumen de información
    const form = document.getElementById('clinicaPersonalForm');
    const resumenInfo = document.getElementById('resumenInfo');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Aquí puedes agregar el código para enviar el formulario
        alert('Formulario enviado correctamente');
    });
    
    // Actualizar vista previa cuando cambian los campos
    form.addEventListener('input', function() {
        updateSummary();
    });
    
    function updateSummary() {
        const formData = new FormData(form);
        let summaryHTML = '';
        
        formData.forEach((value, key) => {
            if (value && key !== 'cv' && key !== 'documentos' && key !== 'terminos') {
                summaryHTML += `<p><strong>${getFieldLabel(key)}:</strong> ${value}</p>`;
            }
        });
        
        resumenInfo.innerHTML = summaryHTML || '<p>No hay información para mostrar</p>';
    }
    
    function getFieldLabel(fieldName) {
        const labels = {
            'name': 'Nombre completo',
            'dni': 'Documento de Identidad',
            'email': 'Correo electrónico',
            'cargo': 'Cargo',
            'departamento': 'Departamento',
            'fecha_ingreso': 'Fecha de ingreso'
        };
        
        return labels[fieldName] || fieldName;
    }
    
    // Mostrar el primer paso al cargar la página
    showStep(1);
});


// Modifica el event listener de nextButtons
nextButtons.forEach(button => {
    button.addEventListener('click', function() {
        const currentStep = parseInt(this.closest('.clinica-form__step').dataset.step);
        const nextStep = parseInt(this.getAttribute('data-next'));
        
        // Validar campos requeridos del paso actual
        const currentStepElement = document.querySelector(`.clinica-form__step[data-step="${currentStep}"]`);
        const requiredInputs = currentStepElement.querySelectorAll('[required]');
        let isValid = true;
        
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                input.style.borderColor = 'var(--clinica-error)';
                isValid = false;
            } else {
                input.style.borderColor = '';
            }
        });
        
        if (isValid) {
            showStep(nextStep);
        } else {
            alert('Por favor complete todos los campos requeridos');
        }
    });
});