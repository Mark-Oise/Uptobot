// Define the initialization function globally
function initializeTabs() {
    // Get all tab buttons
    const tabButtons = document.querySelectorAll('[role="tab"]');

    // Set initial active tab (first tab)
    if (tabButtons.length > 0) {
        tabButtons[0].setAttribute('aria-selected', 'true');
        const firstTabTarget = document.querySelector(tabButtons[0].getAttribute('data-tabs-target'));
        if (firstTabTarget) {
            firstTabTarget.classList.remove('hidden');
        }
    }

    // Add click event listeners to all tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active state from all tabs
            tabButtons.forEach(tab => {
                tab.setAttribute('aria-selected', 'false');
                const target = document.querySelector(tab.getAttribute('data-tabs-target'));
                if (target) {
                    target.classList.add('hidden');
                }
            });

            // Set active state for clicked tab
            button.setAttribute('aria-selected', 'true');
            const target = document.querySelector(button.getAttribute('data-tabs-target'));
            if (target) {
                target.classList.remove('hidden');
            }
        });
    });
}

