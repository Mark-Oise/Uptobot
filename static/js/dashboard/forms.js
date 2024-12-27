/**
 * Handles the interval selection functionality for monitor configuration
 * This code manages both button and range slider inputs for selecting monitoring intervals
 */
function initializeForms() {
    // Get references to DOM elements
    const intervalButtons = document.querySelectorAll('.interval-button');
    const rangeInput = document.getElementById('interval-range-input');
    const currentValueLabel = document.getElementById('current-value');
    const validIntervals = [5, 10, 15, 30, 60];

    // Only proceed if we have the necessary elements on the page
    if (!intervalButtons.length || !rangeInput || !currentValueLabel) return;

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

    // Remove existing event listeners (to prevent duplicates during re-initialization)
    intervalButtons.forEach(button => {
        button.replaceWith(button.cloneNode(true));
    });

    // Re-select buttons after cloning
    document.querySelectorAll('.interval-button').forEach(button => {
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
        interval = validIntervals.reduce((prev, curr) =>
            Math.abs(curr - interval) < Math.abs(prev - interval) ? curr : prev
        );
        this.value = interval;
        currentValueLabel.textContent = `${interval}m`;
        setActiveButton(interval);
    });

    // Alert threshold handling
    const thresholdToggle = document.getElementById('custom_threshold_toggle');
    const thresholdRange = document.getElementById('alert_threshold_range');
    const thresholdValue = document.getElementById('threshold_value');
    const thresholdMessage = document.getElementById('threshold_message');

    if (thresholdToggle && thresholdRange && thresholdValue && thresholdMessage) {
        function updateThresholdUI(isCustom) {
            thresholdRange.disabled = !isCustom;
            thresholdMessage.textContent = isCustom
                ? `Custom threshold: ${thresholdRange.value} seconds`
                : 'Using default threshold (60 seconds)';
            thresholdValue.textContent = `${thresholdRange.value}s`;
        }

        // Remove existing event listeners
        thresholdToggle.replaceWith(thresholdToggle.cloneNode(true));
        thresholdRange.replaceWith(thresholdRange.cloneNode(true));

        // Re-select elements after cloning
        const newThresholdToggle = document.getElementById('custom_threshold_toggle');
        const newThresholdRange = document.getElementById('alert_threshold_range');

        newThresholdToggle.addEventListener('change', function () {
            updateThresholdUI(this.checked);
            if (!this.checked) {
                newThresholdRange.value = 60;
                thresholdValue.textContent = '60s';
            }
        });

        newThresholdRange.addEventListener('input', function () {
            thresholdValue.textContent = `${this.value}s`;
            thresholdMessage.textContent = `Custom threshold: ${this.value} seconds`;
        });

        // Initialize with default state
        updateThresholdUI(newThresholdToggle.checked);
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', initializeForms);

// Make the initialization function available globally
window.initializeForms = initializeForms;