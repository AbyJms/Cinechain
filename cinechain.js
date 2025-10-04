document.addEventListener('DOMContentLoaded', function() {
<<<<<<< HEAD
    
    const sidebarLinks = document.querySelectorAll('.Sidebar a');
    const mainSections = document.querySelectorAll('main > section');
    const sidebarListItems = document.querySelectorAll('.Sidebar li');

    function showSection(targetId) {
        mainSections.forEach(section => {
            if (section.id === targetId) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }

    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            showSection(targetId);
            
            sidebarListItems.forEach(li => li.classList.remove('selected'));
            this.parentElement.classList.add('selected');
        });
    });

    showSection('dashboard');
=======
    // Sidebar selection logic
    const items = document.querySelectorAll('.Sidebar li');
    items.forEach(item => {
        item.addEventListener('click', function() {
            items.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');
        });
    });

    // Utility for random numbers
    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    // Dashboard metrics update
    function updateMetrics() {
        document.getElementById('totalRevenue').textContent = '$' + getRandomInt(50000, 200000).toLocaleString();
        document.getElementById('totalAttendance').textContent = getRandomInt(1000, 10000).toLocaleString();
        document.getElementById('activeChannels').textContent = getRandomInt(5, 100);
        document.getElementById('moviesDistributing').textContent = getRandomInt(10, 50);
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

    // Populate month selector with the last 12 months
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
>>>>>>> a922680360ff67943342ff72036b623817f55acb

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

<<<<<<< HEAD
    const totalRevenueEl = document.getElementById('totalRevenue');
    const totalAttendanceEl = document.getElementById('totalAttendance');
    
    async function updateDashboard() {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/dashboard-data');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();

            totalRevenueEl.textContent = data.totalRevenue;
            totalAttendanceEl.textContent = data.totalAttendance;

            revenueChart.data.labels = data.chartData.labels;
            revenueChart.data.datasets[0].data = data.chartData.data;
            revenueChart.update();
            
        } catch (error) {
            console.error("Could not update dashboard:", error);
        }
    }

    updateDashboard();
    setInterval(updateDashboard, 15000);

});
=======
    monthSelector.addEventListener('change', function() {
        revenueChart.data.datasets[0].data = Array.from({length: 30}, () => getRandomInt(1000, 10000));
        revenueChart.update();
    });
});
>>>>>>> a922680360ff67943342ff72036b623817f55acb
