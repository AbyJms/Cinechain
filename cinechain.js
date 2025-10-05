document.addEventListener('DOMContentLoaded', function() {
    const dashboardBtn = document.getElementById('dashboard-btn');
    const moviesBtn = document.getElementById('movies-btn');
    const dashboardSection = document.getElementById('dashboard');
    const moviesSection = document.getElementById('movies');

    function setActiveSection(section) {
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-button').forEach(b => b.classList.remove('selected'));

        if (section === 'dashboard') {
            dashboardSection.classList.add('active');
            dashboardBtn.classList.add('selected');
        } else if (section === 'movies') {
            moviesSection.classList.add('active');
            moviesBtn.classList.add('selected');
        }
    }

    dashboardBtn.addEventListener('click', () => setActiveSection('dashboard'));
    moviesBtn.addEventListener('click', () => setActiveSection('movies'));

    const initialHash = window.location.hash.substring(1);
    if (initialHash === 'movies') setActiveSection('movies');
    else setActiveSection('dashboard');

    // --- Fetch live data from backend API ---
    async function loadDashboardData() {
        try {
            // 👇 Added timestamp to bypass browser caching
            const res = await fetch('/api/dashboard-data?_=' + new Date().getTime(), {
                cache: 'no-store'
            });
            const data = await res.json();

            console.log("Fetched new data:", data); // 👈 debug log to confirm refresh

            document.getElementById('moviesDistributing').textContent = data.movies_distributing;
            document.getElementById('totalAttendance').textContent = data.total_attendance;
            document.getElementById("totalRevenue").innerText = "₹" + data.total_revenue.toLocaleString("en-IN");

        } catch (err) {
            console.error('Error loading dashboard data:', err);
        }
    }

    // Load data on startup and refresh every 30 seconds
    loadDashboardData();
    setInterval(loadDashboardData, 30000);
});
