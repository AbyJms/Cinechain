document.addEventListener('DOMContentLoaded', function() {
    const dashboardBtn = document.getElementById('dashboard-btn');
    const moviesBtn = document.getElementById('movies-btn');
    const dashboardSection = document.getElementById('dashboard');
    const moviesSection = document.getElementById('movies');
    const moviesContainer = document.getElementById('movies-container');

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

    async function loadDashboardData() {
        try {
            const res = await fetch('/api/dashboard-data');
            const data = await res.json();
            document.getElementById('moviesDistributing').textContent = data.movies_distributing;
            document.getElementById('totalAttendance').textContent = data.total_attendance;
            document.getElementById('totalRevenue').textContent = "₹" + data.total_revenue.toLocaleString();
        } catch (err) {
            console.error('Error loading dashboard data:', err);
        }
    }

    async function loadMoviesData() {
        try {
            const res = await fetch('/api/movies-data');
            const shows = await res.json();

            // Clear previous cards
            moviesContainer.innerHTML = '';

            shows.forEach((show, index) => {
                const card = document.createElement('div');
                card.className = 'card movie-card';
                card.innerHTML = `
                    <div class="movie-info">
                        <h3>Show ${index + 1}</h3>
                        <p>Theatre: <strong>${show.theatre}</strong></p>
                        <p>Movie: <strong>${show.movie}</strong></p>
                        <p>Seats: ${show.seats}</p>
                        <p>Ticket Price: ₹${show.price}</p>
                        <p>Revenue: ₹${show.revenue}</p>
                    </div>
                `;
                moviesContainer.appendChild(card);
            });

        } catch (err) {
            console.error('Error loading movies data:', err);
        }
    }

    loadDashboardData();
    loadMoviesData();
    setInterval(loadDashboardData, 30000);
});
