
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('logo-sidebar');
    const collapseBtn = document.getElementById('sidebar-collapse-btn');
    const sidebarTexts = document.querySelectorAll('.sidebar-text');
    const mainContent = document.getElementById('main-content');
    const tooltipElements = document.querySelectorAll('[role="tooltip"]');
    // Function to set sidebar state in localStorage
    function setSidebarState(collapsed) {
        localStorage.setItem('sidebarCollapsed', collapsed);
    }

    // Function to get sidebar state from localStorage
    function getSidebarState() {
        return localStorage.getItem('sidebarCollapsed') === 'true';
    }

    // Function to update sidebar UI based on state
    function updateSidebarUI(collapsed) {
        if (collapsed) {
            sidebar.classList.remove('w-64');
            sidebar.classList.add('w-16');
            sidebarTexts.forEach(text => text.classList.add('hidden'));
            mainContent.classList.remove('sm:ml-64');
            mainContent.classList.add('sm:ml-16');
            collapseBtn.querySelector('svg').classList.add('rotate-180');

            // Show tooltips
            tooltipElements.forEach(tooltip => {
                tooltip.style.display = 'block';
            });
        } else {
            sidebar.classList.add('w-64');
            sidebar.classList.remove('w-16');
            sidebarTexts.forEach(text => text.classList.remove('hidden'));
            mainContent.classList.add('sm:ml-64');
            mainContent.classList.remove('sm:ml-16');
            collapseBtn.querySelector('svg').classList.remove('rotate-180');

            // Hide tooltips
            tooltipElements.forEach(tooltip => {
                tooltip.style.display = 'none';
            });
        }
    }

    // Initialize sidebar state
    const initialState = getSidebarState();
    updateSidebarUI(initialState);

    collapseBtn.addEventListener('click', function () {
        const newState = !getSidebarState();
        setSidebarState(newState);
        updateSidebarUI(newState);
    });
});










































