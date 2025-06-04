document.getElementById('uploadForm').addEventListener('submit', function(e) {
    const filesInput = document.getElementById('files');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (!filesInput.files.length) {
        e.preventDefault();
        alert('Por favor, selecciona al menos un archivo antes de enviar.');
        return;
    }

    // Deshabilitar el botón y mostrar un efecto de carga
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analizando...';
    analyzeBtn.style.backgroundColor = '#A9A9A9';
});

// Generar gráfica después de cargar la página si hay resultados
window.addEventListener('load', function() {
    const resultsList = JSON.parse('{{ results_list | tojson | safe }}');
    if (resultsList && resultsList.length > 0) {
        const areaCounts = {};
        resultsList.forEach(result => {
            const area = result.prediction;
            areaCounts[area] = (areaCounts[area] || 0) + 1;
        });

        const chartData = {
            type: 'bar',
            data: {
                labels: Object.keys(areaCounts),
                datasets: [{
                    label: 'Número de CVs por Área',
                    data: Object.values(areaCounts),
                    backgroundColor: ['#87CEEB', '#4682B4', '#B0E0E6', '#F0F8FF', '#ADD8E6'],
                    borderColor: ['#4682B4', '#87CEEB', '#ADD8E6', '#B0E0E6', '#F0F8FF'],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Número de CVs'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Áreas'
                        }
                    }
                }
            }
        };

        // Insertar el gráfico en el contenedor
        const chartContainer = document.getElementById('chart-container');
        chartContainer.innerHTML = '<canvas id="cvChart"></canvas>';
        // Simulamos que el gráfico se renderiza (el código real se visualiza como widget)
        console.log('Gráfico generado:', chartData);
    }
});