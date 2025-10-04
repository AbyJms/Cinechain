document.addEventListener('DOMContentLoaded', function() {
    
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
                title: { display: true, text: 'Aggregated Revenue by Theater', font: { size: 24 } }
            },
            scales: {
                x: { title: { display: true, text: 'Theater', font: { size: 18 } } },
                y: { title: { display: true, text: 'Revenue ($)', font: { size: 18 } } }
            }
        }
    });

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