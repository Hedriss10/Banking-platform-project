document.addEventListener("DOMContentLoaded", () => {
    const chart = echarts.init(document.querySelector("#trafficChart"));

    const option = {
        tooltip: {
            trigger: 'item'
        },
        legend: {
            top: '5%',
            left: 'center'
        },
        series: [{
            name: 'Access From',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            label: {
                show: false,
                position: 'center'
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: '18',
                    fontWeight: 'bold'
                }
            },
            labelLine: {
                show: false
            },
            data: [
                { value: 1048, name: 'Sala 102 Contratos' },
                { value: 735, name: 'Contratos Pagos' },
                { value: 580, name: 'Contratos Reprovados' },
                { value: 484, name: 'Erro na digitacão' },
            ]
        }]
    };
    chart.setOption(option);
});