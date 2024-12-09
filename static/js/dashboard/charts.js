// // Store chart instance globally
// let lineChart = null;

// const createChartOptions = (data = {}) => ({
//     chart: {
//         height: "100%",
//         maxWidth: "100%",
//         type: "line",
//         fontFamily: "Inter, sans-serif",
//         dropShadow: {
//             enabled: false,
//         },
//         toolbar: {
//             show: false,
//         },
//     },
//     tooltip: {
//         enabled: true,
//         x: {
//             show: false,
//         },
//     },
//     dataLabels: {
//         enabled: false,
//     },
//     stroke: {
//         width: 6,
//     },
//     grid: {
//         show: true,
//         strokeDashArray: 4,
//         padding: {
//             left: 2,
//             right: 2,
//             top: -26
//         },
//     },
//     series: data.series || [
//         {
//             name: "Response Time (ms)",
//             data: [187, 190, 185, 189, 187, 186],
//             color: "#1A56DB",
//         }
//     ],
//     legend: {
//         show: false
//     },
//     stroke: {
//         curve: 'smooth'
//     },
//     xaxis: {
//         categories: data.categories || ['09 Feb', '10 Feb', '11 Feb', '12 Feb', '13 Feb', '14 Feb'],
//         labels: {
//             show: true,
//             style: {
//                 fontFamily: "Inter, sans-serif",
//                 cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
//             }
//         },
//         axisBorder: {
//             show: false,
//         },
//         axisTicks: {
//             show: false,
//         },
//     },
//     yaxis: {
//         show: false,
//     },
// });

// window.initializeChart = function (data) {
//     const chartElement = document.getElementById("line-chart");
//     if (!chartElement || typeof ApexCharts === 'undefined') return;

//     // Destroy existing chart if it exists
//     if (lineChart) {
//         lineChart.destroy();
//     }

//     // Create new chart
//     lineChart = new ApexCharts(chartElement, createChartOptions(data));
//     lineChart.render();
// };



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
