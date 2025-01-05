function initializeForms() {
    // Config values
    const validIntervals = [5, 10, 15, 30, 60];
    const defaultInterval = 5;

    // Get DOM elements
    const intervalButtons = document.querySelectorAll('.interval-button');
    const rangeInput = document.getElementById('interval-range-input');
    const currentValueLabel = document.getElementById('current-value');

    // Set initial interval based on the range input's value (which comes from the monitor)
    const initialInterval = parseInt(rangeInput.value) || defaultInterval;
    updateInterval(initialInterval);

    // Set active interval button style
    function setActiveButton(activeInterval) {
        intervalButtons.forEach(function (btn) {
            const interval = btn.getAttribute('data-interval');
            if (interval === String(activeInterval)) {
                btn.classList.remove('bg-white', 'text-gray-900', 'dark:bg-gray-800', 'dark:text-gray-400');
                btn.classList.add('bg-gray-800', 'text-white');
            } else {
                btn.classList.remove('bg-gray-800', 'text-white');
                btn.classList.add('bg-white', 'text-gray-900', 'dark:bg-gray-800', 'dark:text-gray-400');
            }
        });
    }

    // Update interval display
    function updateInterval(interval) {
        rangeInput.value = interval;
        currentValueLabel.textContent = interval + 'm';
        setActiveButton(interval);
    }

    // Find closest valid interval
    function snapToValidInterval(value) {
        let closest = validIntervals[0];
        let smallestDiff = Math.abs(validIntervals[0] - value);

        for (let i = 1; i < validIntervals.length; i++) {
            let diff = Math.abs(validIntervals[i] - value);
            if (diff < smallestDiff) {
                smallestDiff = diff;
                closest = validIntervals[i];
            }
        }
        return closest;
    }

    // Add event listeners
    intervalButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const interval = parseInt(button.getAttribute('data-interval'), 10);
            updateInterval(interval);
        });
    });

    rangeInput.addEventListener('input', function (e) {
        const interval = snapToValidInterval(parseInt(e.target.value, 10));
        updateInterval(interval);
    });
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initializeForms);
