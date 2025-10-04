document.addEventListener('DOMContentLoaded', function() {
    const dashboardBtn = document.getElementById('dashboard-btn');
    const moviesBtn = document.getElementById('movies-btn');
    const dashboardSection = document.getElementById('dashboard');
    const moviesSection = document.getElementById('movies');

    // Navigation and section display logic
    function setActiveSection(section) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        // Remove 'selected' from all buttons
        document.querySelectorAll('.nav-button').forEach(b => b.classList.remove('selected'));

        // Show the active section
        if (section === 'dashboard') {
            dashboardSection.classList.add('active');
            dashboardBtn.classList.add('selected');
        } else if (section === 'movies') {
            moviesSection.classList.add('active');
            moviesBtn.classList.add('selected');
        }
    }

    // Event Listeners for buttons
    dashboardBtn.addEventListener('click', () => setActiveSection('dashboard'));
    moviesBtn.addEventListener('click', () => setActiveSection('movies'));

    // Check URL hash to set initial active section
    const initialHash = window.location.hash.substring(1);
    if (initialHash === 'movies') {
        setActiveSection('movies');
    } else {
        // Default to dashboard and ensure URL matches
        setActiveSection('dashboard');
    }

    // --- Metric and Chart Logic Removal/Simplification ---
    // The metrics are now hardcoded in the HTML (0, 0, $50)
    // The revenue chart logic is removed, as the 'No revenue data' state is hardcoded.

    // Month Selector: Ensure it has the correct text and is functional (even if it does nothing)
    const monthSelector = document.getElementById('monthSelector');
    // We only need the "This Month" option as per the image.
    // The HTML already contains a single option, so no JS modifications are strictly needed here.

    // Simple scroll-to-section for the button click (optional but good practice)
    document.querySelectorAll('.nav-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = button.id.includes('dashboard') ? 'dashboard' : 'movies';
            // Update hash without scrolling if content is already visible
            history.pushState(null, null, `#${targetId}`);
        });
    });
});
