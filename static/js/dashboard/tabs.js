// static/js/dashboard/tabs.js

document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
});

function initializeTabs() {
    const tabButtons = document.querySelectorAll('[role="tab"]');
    const tabPanels = document.querySelectorAll('[role="tabpanel"]');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
            });

            // Add active class to clicked button
            button.classList.add('active');
            button.setAttribute('aria-selected', 'true');

            // Hide all tab panels
            tabPanels.forEach(panel => {
                panel.classList.add('hidden');
            });

            // Show the selected tab panel
            const targetId = button.getAttribute('data-tabs-target');
            const targetPanel = document.querySelector(targetId);
            if (targetPanel) {
                targetPanel.classList.remove('hidden');
            }
        });
    });

    // Initialize first tab as active
    const firstTab = document.querySelector('[role="tab"]');
    if (firstTab) {
        firstTab.classList.add('active');
        firstTab.setAttribute('aria-selected', 'true');
    }
}