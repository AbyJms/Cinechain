document.addEventListener('DOMContentLoaded', function() {
    const dashboardBtn = document.getElementById('dashboard-btn');
    const moviesBtn = document.getElementById('movies-btn');
    const dashboardSection = document.getElementById('dashboard');
    const moviesSection = document.getElementById('movies');
    const moviesContainer = document.getElementById('movies-container');

    function setActiveSection(section) {
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-button').forEach(b => b.classList.remove('selected'));
        if(section==='dashboard'){dashboardSection.classList.add('active'); dashboardBtn.classList.add('selected');}
        else if(section==='movies'){moviesSection.classList.add('active'); moviesBtn.classList.add('selected');}
    }

    dashboardBtn.addEventListener('click', ()=>setActiveSection('dashboard'));
    moviesBtn.addEventListener('click', ()=>setActiveSection('movies'));
    const initialHash = window.location.hash.substring(1);
    if(initialHash==='movies') setActiveSection('movies'); else setActiveSection('dashboard');

    async function loadDashboardData() {
        try {
            const res = await fetch('/api/dashboard-data');
            const data = await res.json();
            document.getElementById('moviesDistributing').textContent = data.movies_distributing;
            document.getElementById('totalAttendance').textContent = data.total_attendance;
            document.getElementById('totalRevenue').textContent = "₹" + data.total_revenue.toLocaleString();
        } catch(err){console.error(err);}
    }

    async function loadMoviesData() {
        try{
            const res = await fetch('/api/movies-data');
            const shows = await res.json();
            moviesContainer.innerHTML='';
            shows.forEach(show=>{
                const card = document.createElement('div');
                card.className='card';
                card.innerHTML=`
                    <div class="movie-info">
                        <h3>${show.movie}</h3>
                        <p>Theatre: ${show.theatre}</p>
                        <p>Seats: ${show.seats}</p>
                        <p>Ticket Price: ₹${show.price}</p>
                        <p>Revenue: ₹${show.revenue}</p>
                    </div>
                `;
                moviesContainer.appendChild(card);
            });
        } catch(err){console.error(err);}
    }

    loadDashboardData();
    loadMoviesData();
    setInterval(loadDashboardData,30000);
});

// CSV and Chart
let chartInstance=null; let parsedData=[]; let isDataLoaded=false;

function getTheaterKey(name){const n=String(name).toLowerCase(); if(n.includes('pvr')) return 'PVR'; if(n.includes('vanitha')) return 'VANITHA'; if(n.includes('four star')) return 'FOUR STAR'; return '';}

function groupDataByDate(data){
    const map={};
    data.forEach(r=>{
        const d=String(r.Timestamp).split(' ')[0];
        const rev=parseFloat(r.Revenue)||0;
        if(!map[d]) map[d]=0;
        map[d]+=rev;
    });
    return Object.keys(map).map(d=>({date:d,totalRevenue:map[d]})).sort((a,b)=>new Date(a.date)-new Date(b.date));
}

function processCSV(csvString){
    Papa.parse(csvString,{header:true,dynamicTyping:true,skipEmptyLines:true,complete:function(results){
        parsedData=results.data.filter(r=>r.Timestamp && r.Theatre && r['Movie Name'] && r.Revenue!==undefined && r.Revenue!==null);
        const title=document.getElementById('chart-title');
        const select=document.getElementById('theater-select');
        if(parsedData.length>0){isDataLoaded=true; updateDashboard(select.value); title.textContent=`Revenue Trend for ${select.value} (Daily)`; select.disabled=false;}
        else{isDataLoaded=false; title.textContent="No valid CSV data"; select.disabled=true; if(chartInstance) chartInstance.destroy(); chartInstance=null;}
    },error:function(err){console.error(err);document.getElementById('chart-title').textContent="Error parsing CSV";}});
}

async function fetchCSVData(){
    try{
        const res=await fetch('bms_seatdata.csv');
        const text=await res.text();
        processCSV(text);
    }catch(err){console.error(err); document.getElementById('chart-title').textContent="Failed to load CSV"; document.getElementById('theater-select').disabled=true;}
}

function updateDashboard(theater){
    if(!isDataLoaded) return;
    const filtered=parsedData.filter(r=>getTheaterKey(r.Theatre)===theater);
    document.getElementById('chart-title').textContent=`Revenue Trend for ${theater} (Daily)`;
    updateChart(filtered,theater);
}

function updateChart(data,theater){
    const daily=groupDataByDate(data);
    const labels=daily.map(d=>d.date);
    const revs=daily.map(d=>d.totalRevenue);
    const ctx=document.getElementById('revenueLineChart').getContext('2d');
    const chartData={labels:labels,datasets:[{label:`Daily Revenue (${theater})`,data:revs,borderColor:'#4f46e5',backgroundColor:'rgba(79,70,229,0.2)',pointBackgroundColor:'#4f46e5',tension:0.4,fill:true}]};
    const options={responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true},tooltip:{callbacks:{label:c=>`₹${c.parsed.y.toLocaleString()}`,title:c=>new Date(c[0].label).toLocaleDateString()}}},scales:{x:{title:{display:true,text:'Date'}},y:{title:{display:true,text:'Revenue (₹)'}}}};
    if(chartInstance){chartInstance.data=chartData; chartInstance.options=options; chartInstance.update();}
    else{chartInstance=new Chart(ctx,{type:'line',data:chartData,options:options});}
}

document.addEventListener('DOMContentLoaded',function(){fetchCSVData();document.getElementById('theater-select').addEventListener('change',e=>updateDashboard(e.target.value));});
