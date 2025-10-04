document.addEventListener('DOMContentLoaded', function() {
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
