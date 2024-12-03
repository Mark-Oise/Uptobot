// static/js/dashboard/tabs.js

window.initializeTabs = function () {
    const tabButtons = document.querySelectorAll('[role="tab"]');
    const tabPanels = document.querySelectorAll('[role="tabpanel"]');

    // Remove existing listeners
    tabButtons.forEach(button => {
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
    });

    // Add new listeners
    document.querySelectorAll('[role="tab"]').forEach(button => {
        button.addEventListener('click', handleTabClick);
    });

    // Initialize first tab
    const firstTab = document.querySelector('[role="tab"]');
    if (firstTab) {
        setTimeout(() => firstTab.click(), 0);
    }
};

function handleTabClick(event) {
    // Remove active class from all buttons
    const tabButtons = document.querySelectorAll('[role="tab"]');
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
    });

    // Add active class to clicked button
    const button = event.target;
    button.classList.add('active');
    button.setAttribute('aria-selected', 'true');

    // Hide all tab panels
    const tabPanels = document.querySelectorAll('[role="tabpanel"]');
    tabPanels.forEach(panel => {
        panel.classList.add('hidden');
    });

    // Show the selected tab panel
    const targetId = button.getAttribute('data-tabs-target');
    const targetPanel = document.querySelector(targetId);
    if (targetPanel) {
        targetPanel.classList.remove('hidden');
    }
}