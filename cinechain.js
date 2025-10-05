<<<<<<< HEAD
// cinechain.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Sidebar Navigation Logic ---
    const items = document.querySelectorAll('.Sidebar li');
    items.forEach(item => {
        item.addEventListener('click', function() {
            items.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');

            // Hide all sections and show the selected one
            document.querySelectorAll('main section').forEach(section => {
                section.style.display = 'none';
            });
            const targetSectionId = this.querySelector('a').getAttribute('href').substring(1);
            document.getElementById(targetSectionId).style.display = 'block';
        });
    });

    // Initially show the dashboard
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('movies').style.display = 'none';
    document.getElementById('platforms').style.display = 'none';
    document.getElementById('stakeholders').style.display = 'none';

    // --- Data and Metric Updates ---
    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function updateMetrics() {
        document.getElementById('totalRevenue').textContent = '$' + getRandomInt(50000, 200000).toLocaleString();
        document.getElementById('totalAttendance').textContent = getRandomInt(1000, 10000).toLocaleString();
        document.getElementById('activeChannels').textContent = getRandomInt(5, 100);
        document.getElementById('moviesDistributing').textContent = getRandomInt(10, 50);
    }
    updateMetrics();
    setInterval(updateMetrics, 5000);

    // --- Movie Data (as a JavaScript object) ---
    const movies = [{
        title: 'Interstellar',
        revenue: 150000,
        rating: 9.2,
        genre: 'Sci-Fi',
        image: 'images/interstellar.webp'
    }, {
        title: 'Inception',
        revenue: 120000,
        rating: 8.9,
        genre: 'Sci-Fi',
        image: 'images/inception.webp'
    }, {
        title: 'The Dark Knight',
        revenue: 110000,
        rating: 9.0,
        genre: 'Action',
        image: 'images/darkknight.webp'
    }];

    // --- Dynamic Movie Card Generation with AI ---
    const movieSection = document.getElementById('movies');
    movies.forEach(movie => {
        // Use AI functions from ai.js
        const risk = getRiskScore(movie);
        const recommendation = getPlatformRecommendation(movie.genre);

        const cardHtml = `
            <div class="card movie-card">
                <div class="movie-info">
                    <h3>${movie.title}</h3>
                    <p>Revenue: $${movie.revenue.toLocaleString()}</p>
                    <p>Rating: ${movie.rating}/10</p>
                    <p>AI Risk Score: <strong>${risk}</strong></p>
                    <p>AI Platform Rec: <strong>${recommendation}</strong></p>
                </div>
                <img src="${movie.image}" alt="${movie.title} Poster" />
            </div>
        `;
        movieSection.innerHTML += cardHtml;
    });

    // --- Dynamic Platform Card Generation ---
    const platforms = [{
        title: 'Top Platform',
        platform: 'Netflix',
        moviesHosted: 150,
        totalViews: 1200000
    }, {
        title: 'Second Platform',
        platform: 'Amazon Prime',
        moviesHosted: 120,
        totalViews: 950000
    }, {
        title: 'Third Platform',
        platform: 'Disney+',
        moviesHosted: 100,
        totalViews: 800000
    }];

    const platformsSection = document.getElementById('platforms');
    platforms.forEach(platform => {
        const cardHtml = `
            <div class="card">
                <h3>${platform.title}</h3>
                <p>Platform: <strong>${platform.platform}</strong></p>
                <p>Movies Hosted: ${platform.moviesHosted}</p>
                <p>Total Views: ${platform.totalViews.toLocaleString()}</p>
            </div>
        `;
        platformsSection.innerHTML += cardHtml;
    });


    // --- Revenue Chart with AI Predictions ---
    const monthSelector = document.getElementById('monthSelector');
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    for (let i = 0; i < 12; i++) {
        let date = new Date(currentYear, currentMonth - i, 1);
        let value = `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2, '0')}`;
        let text = `${monthNames[date.getMonth()]} ${date.getFullYear()}`;
        let option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        if (i === 0) option.selected = true;
        monthSelector.appendChild(option);
    }

    const ctx = document.getElementById('revenueChart').getContext('2d');
    const days = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`);
    const historicalRevenue = Array.from({ length: 30 }, () => getRandomInt(1000, 10000));
    
    // Call the AI function to get predictions
    const predictedRevenue = predictRevenue(historicalRevenue);
    
    // Create combined labels for historical and predicted data
    const combinedLabels = [...days, ...Array.from({ length: 30 }, (_, i) => `Predicted Day ${i + 1}`)];
    const combinedData = [...historicalRevenue, ...predictedRevenue];

    const revenueChart = new Chart(ctx, {
        type: 'line', // Changed to line chart for better trend visualization
        data: {
            labels: combinedLabels,
            datasets: [{
                label: 'Actual & Predicted Revenue',
                data: combinedData,
                backgroundColor: 'rgba(46, 83, 201, 0.7)',
                borderColor: 'rgba(46, 83, 201, 1)',
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: false,
            plugins: {
                legend: { display: true },
                title: {
                    display: true,
                    text: 'Monthly Revenue Trend with AI Predictions',
                    font: { size: 24 }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: { display: true, text: 'Day of Month', font: { size: 18 } },
                    grid: { color: '#cfdef3' }
                },
                y: {
                    display: true,
                    title: { display: true, text: 'Revenue ($)', font: { size: 18 } },
                    grid: { color: '#cfdef3' }
                }
            }
=======
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
>>>>>>> 980f2fd04e6bc63514c79d6eb5870701b7e444e7
        }
    }

<<<<<<< HEAD
    monthSelector.addEventListener('change', function() {
        const newHistoricalData = Array.from({ length: 30 }, () => getRandomInt(1000, 10000));
        const newPredictedData = predictRevenue(newHistoricalData);
        revenueChart.data.datasets[0].data = [...newHistoricalData, ...newPredictedData];
        revenueChart.update();
    });
});
=======
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

            moviesContainer.innerHTML = '';

            shows.forEach((show, index) => {
                const card = document.createElement('div');
                card.className = 'card movie-card';
                card.innerHTML = `
                    <div class="movie-info">
                        <h3>${show.movie}</h3>
                        <p>Theatre: <strong>${show.theatre}</strong></p>
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
>>>>>>> 980f2fd04e6bc63514c79d6eb5870701b7e444e7
