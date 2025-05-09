
// Clean up any existing chart instance
if (window.currentChart) {
    window.currentChart.destroy();
}

// Create new chart
if (document.getElementById("labels-chart") && typeof ApexCharts !== 'undefined') {
    window.currentChart = new ApexCharts(document.getElementById("labels-chart"), {
        xaxis: {
            show: true,
            categories: {{ chart_data.dates | safe }},
labels: {
    show: true,
        style: {
        fontFamily: "Inter, sans-serif",
            cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
    }
},
axisBorder: {
    show: false,
                },
axisTicks: {
    show: false,
                },
            },
yaxis: {
    show: true,
        labels: {
        show: true,
            style: {
            fontFamily: "Inter, sans-serif",
                cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
        },
    }
},
series: [{
    name: "Response time (ms)",
    data: {{ chart_data.data | safe }},
    color: "#1A56DB",
            }],
    chart: {
    sparkline: {
        enabled: false
    },
    height: "100%",
        width: "100%",
            type: "area",
                fontFamily: "Inter, sans-serif",
                    dropShadow: {
        enabled: false,
                },
    toolbar: {
        show: false,
                },
},
tooltip: {
    enabled: true,
        x: {
        show: true,
                },
},
fill: {
    type: "gradient",
        gradient: {
        opacityFrom: 0.55,
            opacityTo: 0,
                shade: "#1C64F2",
                    gradientToColors: ["#1C64F2"],
                },
},
dataLabels: {
    enabled: false,
            },
stroke: {
    width: 6,
            },
legend: {
    show: false
},
grid: {
    show: false,
            },
        });
window.currentChart.render();
    }
