
// Define the chart options
const chartOptions = {
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
series: [
    {
        name: "Response time (ms)",
        data: {{ chart_data.data | safe }},
    color: "#1A56DB",
                            },
],
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
                    };

// Keep track of the chart instance
let chartInstance = null;

// Function to initialize the chart
function initializeChart() {
    const chartElement = document.getElementById("labels-chart");

    if (chartElement && typeof ApexCharts !== 'undefined') {
        // Destroy existing chart if it exists
        if (chartInstance) {
            chartInstance.destroy();
        }

        // Create new chart
        chartInstance = new ApexCharts(chartElement, chartOptions);
        chartInstance.render();
    } else {
        // If ApexCharts isn't loaded yet, wait and try again
        setTimeout(initializeChart, 100);
    }
}

// Initialize chart when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChart);
} else {
    initializeChart();
}

// Also initialize when this content is swapped via HTMX
document.addEventListener("htmx:afterSwap", function () {
    initializeChart();
});
