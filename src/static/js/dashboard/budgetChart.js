document.addEventListener("DOMContentLoaded", () => {
    var budgetChart = echarts.init(document.querySelector("#budgetChart")).setOption({
        legend: {
            data: ['Allocated Budget', 'Actual Spending']
        },
        radar: {
            // shape: 'circle',
            indicator: [{
                name: 'Salas',
                max: 6500
            },
            {
                name: 'Administrador',
                max: 16000
            },
            {
                name: 'Operacional',
                max: 30000
            },
            {
                name: 'Suporte',
                max: 38000
            },
            {
                name: 'Campanhas',
                max: 52000
            },
            {
                name: 'Financeiro ',
                max: 25000
            }
            ]
        },
        series: [{
            name: 'Budget vs spending',
            type: 'radar',
            data: [{
                value: [4200, 3000, 20000, 35000, 50000, 18000],
                name: 'Setor interno Budget'
            },
            {
                value: [5000, 14000, 28000, 26000, 42000, 21000],
                name: 'Atual Spending'
            }
            ]
        }]
    });
});