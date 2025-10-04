
document.addEventListener('DOMContentLoaded', function() {
    const items = document.querySelectorAll('.Sidebar li');
    items.forEach(item => {
        item.addEventListener('click', function() {
            items.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');
        });
    });


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


    const monthSelector = document.getElementById('monthSelector');
    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
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
    const days = Array.from({length: 30}, (_, i) => `Day ${i+1}`);
    const revenueData = Array.from({length: 30}, () => getRandomInt(1000, 10000));

    const revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: days,
            datasets: [{
                label: 'Revenue',
                data: revenueData,
                backgroundColor: days.map(() => 'rgba(46, 83, 201, 0.7)'),
                borderColor: days.map(() => '#ff512f'),
                borderWidth: 2,
                borderRadius: 8,
                hoverBackgroundColor: 'rgba(221,36,118,0.7)'
            }]
        },
        options: {
            responsive: false,
            plugins: {
                legend: { display: true },
                title: {
                    display: true,
                    text: 'Monthly Revenue Trend',
                    font: { size: 24 }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: '#2a5298',
                    titleColor: '#fff',
                    bodyColor: '#fff'
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
        }
    });


    monthSelector.addEventListener('change', function() {
        revenueChart.data.datasets[0].data = Array.from({length: 30}, () => getRandomInt(1000, 10000));
        revenueChart.update();
    });
});



async function sendChat() {
    const input = document.getElementById('chatbot-input').value;
    const windowDiv = document.getElementById('chatbot-window');
    if (!input.trim()) return;
    windowDiv.innerHTML += `<div><strong>You:</strong> ${input}</div>`;

    // Simple AI logic (demo): respond based on keywords
    let reply = "Sorry, I don't understand. Please ask about movies or platforms.";
    if (input.toLowerCase().includes('interstellar')) {
        reply = "Interstellar is a top movie with $150,000 revenue and a 9.2/10 rating.";
    } else if (input.toLowerCase().includes('netflix')) {
        reply = "Netflix is the top platform hosting 150 movies with 1,200,000 total views.";
    } else if (input.toLowerCase().includes('top movie')) {
        reply = "The top movie is Interstellar.";
    } else if (input.toLowerCase().includes('revenue')) {
        reply = "Total revenue is shown on the dashboard. For example, Interstellar made $150,000.";
    }

    windowDiv.innerHTML += `<div><strong>AI:</strong> ${reply}</div>`;
    document.getElementById('chatbot-input').value = '';
}

// ...existing code...
    function updateMetrics() {
        document.getElementById('totalRevenue').textContent = '$' + getRandomInt(50000, 200000).toLocaleString();
        document.getElementById('totalAttendance').textContent = getRandomInt(1000, 10000).toLocaleString();
        document.getElementById('activeChannels').textContent = getRandomInt(5, 100);
        document.getElementById('moviesDistributing').textContent = getRandomInt(10, 50);
        // --- New metrics for Box Office Pulse ---
        document.getElementById('ticketSales').textContent = getRandomInt(1000, 50000).toLocaleString();
        document.getElementById('audienceTrend').textContent = getRandomInt(1, 100) + '%';
    }
// ...existing code...

    // --- Stakeholder Spotlight logic ---
    const stakeholderSelector = document.getElementById('stakeholderSelector');
    const stakeholderReport = document.getElementById('stakeholderReport');
    stakeholderSelector.addEventListener('change', function() {
        const role = this.value;
        let report = '';
        if (role === 'producer') report = 'Producer: View earnings, movie reach, and feedback.';
        if (role === 'distributor') report = 'Distributor: See channel performance and compliance.';
        if (role === 'theater') report = 'Theater Owner: Analyze ticket sales and audience demographics.';
        stakeholderReport.textContent = report;
    });

    // --- Geo-Map Distribution ---
    if (window.L) {
        const map = L.map('geoMap').setView([51.505, -0.09], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        // Example markers
        L.marker([51.5, -0.09]).addTo(map).bindPopup('London Cinema');
        L.marker([40.7, -74.0]).addTo(map).bindPopup('New York Cinema');
        L.marker([35.68, 139.76]).addTo(map).bindPopup('Tokyo Cinema');
    }

    // --- Release Radar alerts ---
    function showReleaseAlert(movie) {
        const releaseAlerts = document.getElementById('releaseAlerts');
        const alertDiv = document.createElement('div');
        alertDiv.textContent = `New Release: ${movie.title} on ${movie.date}`;
        alertDiv.style.background = '#e0eafc';
        alertDiv.style.padding = '8px 12px';
        alertDiv.style.marginBottom = '8px';
        alertDiv.style.borderRadius = '8px';
        releaseAlerts.appendChild(alertDiv);
    }
    // Example alerts
    showReleaseAlert({title: 'Tenet', date: '2025-10-10'});
    showReleaseAlert({title: 'Dune', date: '2025-11-05'});



document.addEventListener('DOMContentLoaded', function() {
    // Sidebar selection logic
    const items = document.querySelectorAll('.Sidebar li');
    items.forEach(item => {
        item.addEventListener('click', function() {
            items.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');
        });
    });

    // Utility
    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    // Dashboard metrics update
    function updateMetrics() {
        document.getElementById('totalRevenue').textContent = '$' + getRandomInt(50000, 200000).toLocaleString();
        document.getElementById('totalAttendance').textContent = getRandomInt(1000, 10000).toLocaleString();
        document.getElementById('activeChannels').textContent = getRandomInt(5, 100);
        document.getElementById('moviesDistributing').textContent = getRandomInt(10, 50);
        // Box Office Pulse metrics
        document.getElementById('ticketSales').textContent = getRandomInt(1000, 50000).toLocaleString();
        document.getElementById('audienceTrend').textContent = getRandomInt(1, 100) + '%';
    }
    updateMetrics();
    setInterval(updateMetrics, 5000);

    // Revenue chart logic
    const monthSelector = document.getElementById('monthSelector');
    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
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
    const days = Array.from({length: 30}, (_, i) => `Day ${i+1}`);
    const revenueData = Array.from({length: 30}, () => getRandomInt(1000, 10000));
    const revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: days,
            datasets: [{
                label: 'Revenue',
                data: revenueData,
                backgroundColor: days.map(() => 'rgba(46, 83, 201, 0.7)'),
                borderColor: days.map(() => '#ff512f'),
                borderWidth: 2,
                borderRadius: 8,
                hoverBackgroundColor: 'rgba(221,36,118,0.7)'
            }]
        },
        options: {
            responsive: false,
            plugins: {
                legend: { display: true },
                title: {
                    display: true,
                    text: 'Monthly Revenue Trend',
                    font: { size: 24 }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: '#2a5298',
                    titleColor: '#fff',
                    bodyColor: '#fff'
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
        }
    });
    monthSelector.addEventListener('change', function() {
        revenueChart.data.datasets[0].data = Array.from({length: 30}, () => getRandomInt(1000, 10000));
        revenueChart.update();
    });

    // Stakeholder Spotlight logic
    const stakeholderSelector = document.getElementById('stakeholderSelector');
    const stakeholderReport = document.getElementById('stakeholderReport');
    stakeholderSelector.addEventListener('change', function() {
        const role = this.value;
        let report = '';
        if (role === 'producer') report = 'Producer: View earnings, movie reach, and feedback.';
        if (role === 'distributor') report = 'Distributor: See channel performance and compliance.';
        if (role === 'theater') report = 'Theater Owner: Analyze ticket sales and audience demographics.';
        stakeholderReport.textContent = report;
    });

    // Geo-Map Distribution
    if (window.L) {
        const map = L.map('geoMap').setView([51.505, -0.09], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        L.marker([51.5, -0.09]).addTo(map).bindPopup('London Cinema');
        L.marker([40.7, -74.0]).addTo(map).bindPopup('New York Cinema');
        L.marker([35.68, 139.76]).addTo(map).bindPopup('Tokyo Cinema');
    }

    // Release Radar alerts
    function showReleaseAlert(movie) {
        const releaseAlerts = document.getElementById('releaseAlerts');
        const alertDiv = document.createElement('div');
        alertDiv.textContent = `New Release: ${movie.title} on ${movie.date}`;
        alertDiv.style.background = '#e0eafc';
        alertDiv.style.padding = '8px 12px';
        alertDiv.style.marginBottom = '8px';
        alertDiv.style.borderRadius = '8px';
        releaseAlerts.appendChild(alertDiv);
    }
    showReleaseAlert({title: 'Tenet', date: '2025-10-10'});
    showReleaseAlert({title: 'Dune', date: '2025-11-05'});
});

