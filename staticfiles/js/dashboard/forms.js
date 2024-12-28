function initializeForms() {
    // Config values
    const validIntervals = [5, 10, 15, 30, 60];
    const defaultInterval = 5;
    const defaultThreshold = 60;

    // Get DOM elements
    const intervalButtons = document.querySelectorAll('.interval-button');
    const rangeInput = document.getElementById('interval-range-input');
    const currentValueLabel = document.getElementById('current-value');
    const thresholdToggle = document.getElementById('custom_threshold_toggle');
    const thresholdRange = document.getElementById('alert_threshold_range');
    const thresholdValue = document.getElementById('threshold_value');
    const thresholdMessage = document.getElementById('threshold_message');

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

    // Update threshold display
    function updateThresholdUI(isCustom) {
        thresholdRange.disabled = !isCustom;
        thresholdValue.textContent = thresholdRange.value + 's';
        thresholdMessage.textContent = isCustom
            ? 'Custom threshold: ' + thresholdRange.value + ' seconds'
            : 'Using default threshold (' + defaultThreshold + ' seconds)';
    }

    // Set initial interval
    updateInterval(defaultInterval);

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

    thresholdToggle.addEventListener('change', function (e) {
        updateThresholdUI(e.target.checked);
        if (!e.target.checked) {
            thresholdRange.value = defaultThreshold;
        }
    });

    thresholdRange.addEventListener('input', function () {
        updateThresholdUI(true);
    });

    // Initialize threshold UI
    updateThresholdUI(thresholdToggle.checked);
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initializeForms);