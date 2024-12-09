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
