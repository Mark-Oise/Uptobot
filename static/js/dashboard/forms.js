/**
 * Handles the interval selection functionality for monitor configuration
 * This code manages both button and range slider inputs for selecting monitoring intervals
 */
document.addEventListener('DOMContentLoaded', function () {
    // Get references to DOM elements
    const intervalButtons = document.querySelectorAll('.interval-button'); // Interval selection buttons
    const rangeInput = document.getElementById('interval-range-input'); // Range slider input
    const currentValueLabel = document.getElementById('current-value'); // Label showing current interval value
    const validIntervals = [5, 10, 15, 30, 60]; // Valid interval values in minutes

    /**
     * Updates the visual state of interval buttons based on selected interval
     * @param {number} activeInterval - The currently selected interval value
     */
    function setActiveButton(activeInterval) {
        intervalButtons.forEach(btn => {
            const interval = btn.getAttribute('data-interval');
            if (interval === String(activeInterval)) {
                // Add active state classes
                btn.classList.remove('bg-white', 'text-gray-900', 'dark:bg-gray-800', 'dark:text-gray-400');
                btn.classList.add('bg-gray-800', 'text-white');
            } else {
                // Add inactive state classes
                btn.classList.remove('bg-gray-800', 'text-white');
                btn.classList.add('bg-white', 'text-gray-900', 'dark:bg-gray-800', 'dark:text-gray-400');
            }
        });
    }

    // Initialize with 5 minute interval selected
    setActiveButton(5);

    // Add click handlers to interval buttons
    intervalButtons.forEach(button => {
        button.addEventListener('click', function () {
            const interval = parseInt(this.getAttribute('data-interval'), 10);
            rangeInput.value = interval;
            currentValueLabel.textContent = `${interval}m`;
            setActiveButton(interval);
        });
    });

    // Handle range slider input changes
    rangeInput.addEventListener('input', function () {
        let interval = parseInt(this.value, 10);
        // Snap to nearest valid interval
        interval = validIntervals.reduce((prev, curr) => 
            Math.abs(curr - interval) < Math.abs(prev - interval) ? curr : prev
        );
        this.value = interval;
        currentValueLabel.textContent = `${interval}m`;
        setActiveButton(interval);
    });
});