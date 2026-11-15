// Gráficos (Chart.js) no tema carvão e champanhe. Cada função recebe o id do <canvas> e os dados.
(function () {
    var CHAMP = '#d6be96', CHAMP_ESC = '#8a7654', LINHA = '#2e2f34', TEXTO = '#9a958c';
    var PALETA = ['#d6be96', '#8fb39b', '#8aa4c2', '#cf7a73', '#d3a85f'];

    if (window.Chart) {
        Chart.defaults.font.family = '"Jost", system-ui, sans-serif';
        Chart.defaults.color = TEXTO;
        Chart.defaults.borderColor = LINHA;
    }

    function moeda(v) { return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }); }

    // Barras empilhadas: faturamento (itens) + taxa de serviço, por dia
    window.graficoDias = function (id, dados) {
        new Chart(document.getElementById(id), {
            type: 'bar',
            data: {
                labels: dados.rotulos.map(function (r) { return r.split(' '); }),
                datasets: [
                    { label: 'Itens', data: dados.faturamento, backgroundColor: CHAMP, borderRadius: 0, maxBarThickness: 38 },
                    { label: 'Taxa de serviço', data: dados.taxas, backgroundColor: CHAMP_ESC, borderRadius: 0, maxBarThickness: 38 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    x: { stacked: true, grid: { display: false }, ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 15 } },
                    y: { stacked: true, beginAtZero: true, ticks: { callback: function (v) { return moeda(v).replace(',00', ''); } } }
                },
                plugins: {
                    legend: { position: 'bottom', labels: { usePointStyle: true, pointStyle: 'rect', boxWidth: 8 } },
                    tooltip: { callbacks: { label: function (c) { return ' ' + c.dataset.label + ': ' + moeda(c.parsed.y); } } }
                }
            }
        });
    };

    // Rosca: participação das formas de pagamento
    window.graficoFormas = function (id, formas) {
        new Chart(document.getElementById(id), {
            type: 'doughnut',
            data: {
                labels: formas.map(function (f) { return f.rotulo; }),
                datasets: [{ data: formas.map(function (f) { return f.valor; }), backgroundColor: PALETA, borderColor: '#1a1b1e', borderWidth: 3 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '68%',
                plugins: {
                    legend: { position: 'bottom', labels: { usePointStyle: true, pointStyle: 'rect', boxWidth: 8 } },
                    tooltip: { callbacks: { label: function (c) { return ' ' + c.label + ': ' + moeda(c.parsed); } } }
                }
            }
        });
    };
})();
