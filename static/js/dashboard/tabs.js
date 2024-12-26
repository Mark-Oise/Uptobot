// Move the initialization logic into a named function
window.initializeTabs = function () {
    const tabButtons = document.querySelectorAll('[role="tab"]');
    const tabPanels = document.querySelectorAll('[role="tabpanel"]');

    // Set initial state
    if (tabButtons.length > 0) {
        tabButtons[0].setAttribute('aria-selected', 'true');
        tabPanels[0].classList.remove('hidden');
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Deactivate all tabs
            tabButtons.forEach(btn => {
                btn.setAttribute('aria-selected', 'false');
            });
            tabPanels.forEach(panel => {
                panel.classList.add('hidden');
            });

            // Activate clicked tab
            button.setAttribute('aria-selected', 'true');
            const targetId = button.getAttribute('data-tabs-target').substring(1);
            document.getElementById(targetId).classList.remove('hidden');
        });
    });
};
