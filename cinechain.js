document.addEventListener('DOMContentLoaded', function() {
    
    const sidebarItems = document.querySelectorAll('.Sidebar li');
    sidebarItems.forEach(item => {
        item.addEventListener('click', function() {
            sidebarItems.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');
        });
    });

    const stakeholderSelector = document.getElementById('stakeholderSelector');
    if (stakeholderSelector) {
        const stakeholderReport = document.getElementById('stakeholderReport');
        stakeholderSelector.addEventListener('change', function() {
            const role = this.value;
            let report = '';
            if (role === 'producer') report = 'Producer: View earnings, movie reach, and feedback.';
            if (role === 'distributor') report = 'Distributor: See channel performance and compliance.';
            if (role === 'theater') report = 'Theater Owner: Analyze ticket sales and audience demographics.';
            stakeholderReport.textContent = report;
        });
    }

    const ctx = document.getElementById('revenueChart').getContext('2d');
    const revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Revenue by Theater',
                data: [],
                backgroundColor: 'rgba(46, 83, 201, 0.7)',
                borderColor: '#ff512f',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: false,
            plugins: {
                legend: { display: true },
                title: { display: true, text: 'Real-Time Revenue by Theater', font: { size: 24 } }
            },
            scales: {
                x: { title: { display: true, text: 'Theater', font: { size: 18 } } },
                y: { title: { display: true, text: 'Revenue ($)', font: { size: 18 } } }
            }
        }
    });

    const socket = io.connect('http://127.0.0.1:5000');

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

    socket.on('dashboard_update', (eventData) => {
        console.log('Update received from server:', eventData.message);
        updateDashboard();
    });

    updateDashboard();

});
