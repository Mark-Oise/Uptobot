const AppInit = {
    initializeAll: function () {
        // Initialize Flowbite components
        if (window.initFlowbite) {
            window.initFlowbite();
        }

        // Initialize charts
        if (document.getElementById("labels-chart")) {
            window.initializeChart();
        }

        // Initialize tabs
        if (document.querySelector('[role="tab"]')) {
            window.initializeTabs();
        }
    }
};

// Initialize on first load
document.addEventListener('DOMContentLoaded', AppInit.initializeAll);

// Initialize after every HTMX request
document.addEventListener('htmx:afterSwap', AppInit.initializeAll);
document.addEventListener('htmx:afterSettle', AppInit.initializeAll);