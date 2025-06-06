// Manejo del envío del formulario
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
    analyzeBtn.querySelector('.clinica-reclutamiento__btn-text').textContent = 'Analizando...';
    analyzeBtn.style.backgroundColor = '#A9A9A9';
});

// Generar gráfica y estadísticas al cargar la página
window.addEventListener('load', function() {
    // Obtener datos de resultados nuevos y anteriores desde el servidor
    const resultsList = {{ results_list | tojson | safe }};
    const previousResults = {{ previous_results | tojson | safe }};

    // Calcular estadísticas para el header
    let totalCvs = 0;
    let totalMatches = 0;

    if (resultsList && resultsList.length > 0) {
        totalCvs += resultsList.length;
        resultsList.forEach(result => {
            if (result.results[result.prediction] > 70) totalMatches++;
        });
    }
    if (previousResults && previousResults.length > 0) {
        totalCvs += previousResults.length;
        previousResults.forEach(result => {
            if (result.results[result.prediction] > 70) totalMatches++;
        });
    }

    // Actualizar estadísticas en el header
    document.getElementById('totalUploads').textContent = totalCvs;
    document.getElementById('successfulMatches').textContent = totalMatches;

    // Generar datos para el gráfico
    const areaCounts = {};
    [resultsList, previousResults].forEach(results => {
        if (results && results.length > 0) {
            results.forEach(result => {
                const area = result.prediction;
                areaCounts[area] = (areaCounts[area] || 0) + 1;
            });
        }
    });

    if (Object.keys(areaCounts).length > 0) {
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
        const chartContainer = document.getElementById('areaDistributionChart').parentElement;
        if (chartContainer) {
            const canvas = document.getElementById('areaDistributionChart');
            if (canvas) {
                new Chart(canvas, chartData); // Renderizar el gráfico
            } else {
                chartContainer.innerHTML = '<canvas id="areaDistributionChart"></canvas>';
                new Chart(document.getElementById('areaDistributionChart'), chartData);
            }
        }
    } else {
        const chartContainer = document.getElementById('areaDistributionChart').parentElement;
        if (chartContainer) {
            chartContainer.innerHTML = '<p>No hay datos suficientes para mostrar el gráfico.</p>';
        }
    }

    // Manejo de filtros para resultados nuevos
    const areaFilter = document.getElementById('areaFilter');
    const scoreFilter = document.getElementById('scoreFilter');
    const scoreValue = document.getElementById('scoreValue');
    if (areaFilter && scoreFilter) {
        scoreFilter.addEventListener('input', function() {
            scoreValue.textContent = `${this.value}%`;
            filterResults();
        });

        areaFilter.addEventListener('change', filterResults);

        function filterResults() {
            const minScore = parseInt(scoreFilter.value);
            const selectedArea = areaFilter.value;
            const cards = document.querySelectorAll('.clinica-reclutamiento__result-card');
            cards.forEach(card => {
                const area = card.getAttribute('data-area');
                const score = parseFloat(card.getAttribute('data-score'));
                const matchesArea = selectedArea === 'all' || area === selectedArea;
                const matchesScore = score >= minScore;
                card.style.display = matchesArea && matchesScore ? 'block' : 'none';
            });
        }
    }

    // Manejo de filtros para resultados anteriores
    const areaFilterPrev = document.getElementById('areaFilterPrev');
    const scoreFilterPrev = document.getElementById('scoreFilterPrev');
    const scoreValuePrev = document.getElementById('scoreValuePrev');
    if (areaFilterPrev && scoreFilterPrev) {
        scoreFilterPrev.addEventListener('input', function() {
            scoreValuePrev.textContent = `${this.value}%`;
            filterPreviousResults();
        });

        areaFilterPrev.addEventListener('change', filterPreviousResults);

        function filterPreviousResults() {
            const minScore = parseInt(scoreFilterPrev.value);
            const selectedArea = areaFilterPrev.value;
            const cards = document.querySelectorAll('.clinica-reclutamiento__result-card');
            cards.forEach(card => {
                const area = card.getAttribute('data-area');
                const score = parseFloat(card.getAttribute('data-score'));
                const matchesArea = selectedArea === 'all' || area === selectedArea;
                const matchesScore = score >= minScore;
                card.style.display = matchesArea && matchesScore ? 'block' : 'none';
            });
        }
    }
});