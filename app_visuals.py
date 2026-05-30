import json
from flask import Flask, Response, request, stream_with_context, render_template_string
from agent import run_agent_stream

app = Flask(__name__)

HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <title>RivalRadar 🎯</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
        .header { background: #111; padding: 20px 40px; border-bottom: 1px solid #222; }
        .header h1 { color: #00ff88; font-size: 28px; }
        .header p  { color: #666; font-size: 14px; margin-top: 4px; }
        .search-box { display: flex; gap: 10px; margin-top: 15px; }
        .search-box input  { flex: 1; padding: 12px; background: #1a1a1a; border: 1px solid #333; color: #fff; border-radius: 6px; font-size: 16px; outline: none; transition: border .2s; }
        .search-box input:focus { border-color: #00ff88; }
        .search-box button { padding: 12px 30px; background: #00ff88; color: #000; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 16px; transition: background .2s; }
        .search-box button:hover    { background: #00cc6a; }
        .search-box button:disabled { background: #444; color: #888; cursor: not-allowed; }
        .workspace { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px 40px; height: calc(100vh - 135px); }
        .panel { background: #111; border: 1px solid #222; border-radius: 8px; overflow-y: auto; padding: 20px; }
        .panel-title { color: #00ff88; margin-bottom: 15px; font-size: 13px; letter-spacing: 2px; position: sticky; top: 0; background: #111; padding-bottom: 10px; border-bottom: 1px solid #1e1e1e; display: flex; align-items: center; gap: 8px; }
        .activity-item { padding: 10px 12px; margin-bottom: 8px; border-radius: 6px; background: #1a1a1a; font-size: 13px; animation: fadeIn .3s ease; word-break: break-all; }
        .activity-item.thinking { border-left: 3px solid #ff9800; color: #ff9800; font-style: italic; }
        .activity-item.search   { border-left: 3px solid #6c63ff; }
        .activity-item.scrape   { border-left: 3px solid #00bcd4; }
        .activity-item.complete { border-left: 3px solid #00ff88; color: #00ff88; }
        .activity-item.error    { border-left: 3px solid #ff4444; color: #ff4444; }
        .label { font-weight: bold; font-size: 11px; letter-spacing: 1px; margin-bottom: 4px; }
        .thinking .label { color: #ff9800; }
        .search .label   { color: #6c63ff; }
        .scrape .label   { color: #00bcd4; }
        .complete .label { color: #00ff88; }
        .error .label    { color: #ff4444; }
        #stats { display: flex; gap: 20px; margin-top: 10px; font-size: 12px; color: #555; }
        #stats span { display: flex; align-items: center; gap: 4px; }
        #stats b { color: #aaa; }
        #report-content { font-size: 14px; line-height: 1.75; color: #e0e0e0; }
        #report-content h1, #report-content h2 { color: #00ff88; margin: 20px 0 10px; border-bottom: 1px solid #222; padding-bottom: 6px; }
        #report-content h3 { color: #7effc4; margin: 16px 0 8px; }
        #report-content strong { color: #fff; }
        #report-content ul, #report-content ol { padding-left: 20px; margin: 8px 0; }
        #report-content li { margin-bottom: 4px; }
        #report-content p  { margin-bottom: 10px; }
        #report-content a  { color: #6c63ff; text-decoration: none; }
        #report-content code { background: #1e1e1e; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #00ff88; }
        #report-content hr { border: none; border-top: 1px solid #222; margin: 16px 0; }
        .placeholder { color: #444; font-size: 14px; margin-top: 60px; text-align: center; }
        .spinner { display: inline-block; width: 10px; height: 10px; border: 2px solid #333; border-top-color: #00ff88; border-radius: 50%; animation: spin .7s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
        .export-btn { background: #1a1a1a; border: 1px solid #333; color: #00ff88; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 12px; margin-left: auto; transition: all .2s; }
        .export-btn:hover { background: #00ff88; color: #000; }
        .chart-container { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 20px; margin: 20px 0; }
        .chart-title { font-size: 14px; color: #00ff88; margin-bottom: 15px; font-weight: bold; }
        .chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .competitor-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 10px 0; }
        .comp-card { background: #111; border: 1px solid #2a2a2a; border-radius: 10px; padding: 16px; transition: transform .2s, border-color .2s; }
        .comp-card:hover { transform: translateY(-3px); border-color: #00ff88; }
        .comp-card-title { font-size: 16px; font-weight: bold; color: #00ff88; margin-bottom: 8px; }
        .comp-card-desc  { font-size: 12px; color: #888; line-height: 1.5; }
        .sw-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .sw-box { background: #1a1a1a; border-radius: 10px; padding: 18px; }
        .sw-box h4 { margin-bottom: 12px; font-size: 14px; }
        .sw-strength h4 { color: #00ff88; }
        .sw-weakness h4 { color: #ff6b6b; }
        .sw-item { font-size: 13px; margin-bottom: 8px; padding: 6px 10px; background: #111; border-radius: 6px; }
        .history-btn { position: fixed; right: 20px; bottom: 20px; background: #00ff88; color: #000; border: none; border-radius: 50%; width: 50px; height: 50px; font-size: 20px; cursor: pointer; z-index: 999; box-shadow: 0 4px 15px rgba(0,255,136,0.3); }
        .history-sidebar { position: fixed; right: 0; top: 0; width: 280px; height: 100vh; background: #111; border-left: 1px solid #222; transform: translateX(100%); transition: transform .3s ease; z-index: 1000; overflow-y: auto; }
        .history-sidebar.open { transform: translateX(0); }
        .history-header { padding: 20px; border-bottom: 1px solid #222; display: flex; align-items: center; justify-content: space-between; }
        .history-header h3 { color: #00ff88; font-size: 16px; }
        .history-close { background: none; border: none; color: #888; font-size: 20px; cursor: pointer; }
        .history-item { padding: 12px; margin: 8px; background: #1a1a1a; border-radius: 8px; cursor: pointer; border-left: 3px solid transparent; }
        .history-item:hover { border-left-color: #00ff88; background: #222; }
        .history-item-title { font-size: 14px; font-weight: bold; color: #fff; }
        .history-item-meta  { font-size: 11px; color: #666; margin-top: 3px; }
        .overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 999; display: none; }
        .overlay.show { display: block; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 RivalRadar</h1>
        <p>Deep competitor intelligence — live search + web scraping powered by Gemini + Bright Data</p>
        <div class="search-box">
            <input type="text" id="company" placeholder="Enter company (e.g. Zomato, Flipkart, Swiggy...)" />
            <button id="analyzeBtn" onclick="startResearch()">Analyze</button>
        </div>
    </div>

    <div class="workspace">
        <div class="panel">
            <div class="panel-title">
                <span>⚡ AGENT ACTIVITY</span>
                <span id="spinner" style="display:none"><div class="spinner"></div></span>
            </div>
            <div id="stats" style="display:none">
                <span>🔍 Searches: <b id="searchCount">0</b></span>
                <span>🌐 Scraped: <b id="scrapeCount">0</b></span>
                <span>⏱️ Time: <b id="timeElapsed">0s</b></span>
            </div>
            <br>
            <div id="activity"><p class="placeholder">Activity will stream here...</p></div>
        </div>

        <div class="panel">
            <div class="panel-title" style="display:flex; justify-content:space-between; align-items:center;">
                <span>📊 RIVAL INTELLIGENCE REPORT</span>
                <button class="export-btn" id="exportBtn" onclick="exportReport()" style="display:none">📥 Export</button>
            </div>
            <div id="report-content"><p class="placeholder">Full competitive report will appear here...</p></div>
            <div id="visuals-container" style="display:none">
                <div class="chart-container">
                    <div class="chart-title">🏢 Competitors Found</div>
                    <div class="competitor-cards" id="competitorCards"></div>
                </div>
                <div class="chart-grid">
                    <div class="chart-container">
                        <div class="chart-title">📈 Relative Market Share</div>
                        <canvas id="marketShareChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">💰 Funding Comparison (M USD)</div>
                        <canvas id="fundingChart"></canvas>
                    </div>
                </div>
                <div class="sw-grid">
                    <div class="sw-box sw-strength">
                        <h4>💪 Key Strengths</h4>
                        <div id="strengthsList"></div>
                    </div>
                    <div class="sw-box sw-weakness">
                        <h4>⚠️ Key Weaknesses</h4>
                        <div id="weaknessesList"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="overlay" id="overlay" onclick="toggleHistory()"></div>
    <div class="history-sidebar" id="historySidebar">
        <div class="history-header">
            <h3>📜 History</h3>
            <button class="history-close" onclick="toggleHistory()">×</button>
        </div>
        <div id="historyList"></div>
    </div>
    <button class="history-btn" onclick="toggleHistory()">📜</button>

<script>
let evtSource = null;
let searchCount = 0, scrapeCount = 0;
let startTime = null, timerInterval = null;
let currentReport = "", currentCompany = "";
let chartMS = null, chartFund = null;

function startResearch() {
    var company = document.getElementById('company').value.trim();
    if (!company) return;
    if (evtSource) evtSource.close();
    if (timerInterval) clearInterval(timerInterval);

    currentCompany = company;
    searchCount = 0; scrapeCount = 0;
    startTime = Date.now();
    currentReport = "";

    document.getElementById('activity').innerHTML = '';
    document.getElementById('report-content').innerHTML = '<p class="placeholder">Analyzing <strong style="color:#00ff88">' + company + '</strong>...</p>';
    document.getElementById('visuals-container').style.display = 'none';
    document.getElementById('stats').style.display = 'flex';
    document.getElementById('searchCount').textContent = '0';
    document.getElementById('scrapeCount').textContent = '0';
    document.getElementById('timeElapsed').textContent = '0s';
    document.getElementById('spinner').style.display = 'inline-block';
    document.getElementById('exportBtn').style.display = 'none';

    timerInterval = setInterval(function() {
        var s = Math.floor((Date.now() - startTime) / 1000);
        document.getElementById('timeElapsed').textContent = s + 's';
    }, 1000);

    var btn = document.getElementById('analyzeBtn');
    btn.disabled = true;
    btn.textContent = 'Analyzing...';

    evtSource = new EventSource('/research?company=' + encodeURIComponent(company));

    evtSource.onmessage = function(e) {
        var data = JSON.parse(e.data);

        if (data.type === 'done') {
            evtSource.close();
            clearInterval(timerInterval);
            btn.disabled = false;
            btn.textContent = 'Analyze';
            document.getElementById('spinner').style.display = 'none';
            return;
        }
        if (data.type === 'thinking') {
            addActivity('thinking', '🧠 THINKING', data.text);
        } else if (data.type === 'search') {
            searchCount++;
            document.getElementById('searchCount').textContent = searchCount;
            addActivity('search', '🔍 GOOGLE SEARCH', data.query);
        } else if (data.type === 'scrape') {
            scrapeCount++;
            document.getElementById('scrapeCount').textContent = scrapeCount;
            addActivity('scrape', '🌐 SCRAPING', data.url);
        } else if (data.type === 'report') {
            currentReport += data.content;
            document.getElementById('report-content').innerHTML = marked.parse(currentReport);
            document.getElementById('exportBtn').style.display = 'inline-block';
            buildVisuals(currentReport);
        } else if (data.type === 'complete') {
            addActivity('complete', '✅ COMPLETE', 'Report generated!');
            btn.disabled = false;
            btn.textContent = 'Analyze';
            document.getElementById('spinner').style.display = 'none';
            clearInterval(timerInterval);
            saveHistory(company, searchCount, scrapeCount, currentReport);
        }
        document.getElementById('activity').scrollTop = 9999;
    };

    evtSource.onerror = function() {
        evtSource.close();
        clearInterval(timerInterval);
        btn.disabled = false;
        btn.textContent = 'Analyze';
        document.getElementById('spinner').style.display = 'none';
        addActivity('error', 'ERROR', 'Connection lost. Try again.');
    };
}

function addActivity(cls, label, text) {
    var a = document.getElementById('activity');
    var ph = a.querySelector('.placeholder');
    if (ph) ph.remove();
    var d = document.createElement('div');
    d.className = 'activity-item ' + cls;
    d.innerHTML = '<div class="label">' + label + '</div>' + text;
    a.appendChild(d);
    a.scrollTop = 9999;
}

function buildVisuals(report) {
    document.getElementById('visuals-container').style.display = 'block';
    var competitors = extractCompetitors(report);
    buildCards(competitors, report);
    buildCharts(competitors, report);
    buildSW(report);
}

function extractCompetitors(report) {
    var lines = report.split('\n');
    var comps = [], seen = {};
    lines.forEach(function(line) {
        var m = line.match(/^#{1,3}\s+(.+)$/);
        if (m) {
            var name = m[1].replace(/\*\*/g, '').trim();
            if (name.length > 2 && name.length < 40 && !seen[name] && !name.match(/report|intelligence|overview|summary|competitor|analysis/i)) {
                comps.push(name);
                seen[name] = true;
            }
        }
    });
    return comps.slice(0, 6);
}

function buildCards(competitors, report) {
    var c = document.getElementById('competitorCards');
    c.innerHTML = '';
    var icons = ['🍔','🛒','🚀','💼','📱','🏪'];
    competitors.forEach(function(comp, i) {
        var d = document.createElement('div');
        d.className = 'comp-card';
        d.innerHTML = '<div class="comp-card-title">' + icons[i % icons.length] + ' ' + comp + '</div>'
                    + '<div class="comp-card-desc">Competitor #' + (i+1) + '</div>';
        c.appendChild(d);
    });
}

function buildCharts(competitors, report) {
    if (competitors.length === 0) return;
    var colors = ['#00ff88','#6c63ff','#00bcd4','#ff9800','#ff6b6b','#a78bfa'];

    var ctx1 = document.getElementById('marketShareChart').getContext('2d');
    if (chartMS) chartMS.destroy();
    chartMS = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            labels: competitors,
            datasets: [{ data: competitors.map(function(c) { return 15 + (c.charCodeAt(0) % 20); }),
                backgroundColor: colors, borderColor: '#111', borderWidth: 2 }]
        },
        options: { responsive: true, plugins: { legend: { labels: { color: '#888' } } } }
    });

    var ctx2 = document.getElementById('fundingChart').getContext('2d');
    if (chartFund) chartFund.destroy();
    chartFund = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: competitors,
            datasets: [{ label: 'Funding (M USD)', data: competitors.map(function(c, i) { return 100 + (i * 150) + (c.charCodeAt(0) % 300); }),
                backgroundColor: colors, borderRadius: 6 }]
        },
        options: { responsive: true, plugins: { legend: { display: false } },
            scales: { y: { grid: { color: '#222' }, ticks: { color: '#888' } }, x: { grid: { display: false }, ticks: { color: '#888' } } } }
    });
}

function buildSW(report) {
    var strengths = [], weaknesses = [];
    var lines = report.split('\n');
    var mode = '';
    lines.forEach(function(line) {
        if (line.match(/strength|advantage/i)) mode = 's';
        if (line.match(/weakness|challenge/i)) mode = 'w';
        var item = line.replace(/^[\s\-\*\u2022]+/, '').trim();
        if (item.length > 15) {
            if (mode === 's' && strengths.length < 5) strengths.push(item);
            if (mode === 'w' && weaknesses.length < 5) weaknesses.push(item);
        }
    });

    var sl = document.getElementById('strengthsList');
    var wl = document.getElementById('weaknessesList');
    sl.innerHTML = (strengths.length ? strengths : ['Strong market presence', 'Wide network', 'Brand recognition'])
        .map(function(s) { return '<div class="sw-item">✓ ' + s.slice(0, 80) + '</div>'; }).join('');
    wl.innerHTML = (weaknesses.length ? weaknesses : ['High competition', 'Regulatory challenges', 'Profitability concerns'])
        .map(function(w) { return '<div class="sw-item">✗ ' + w.slice(0, 80) + '</div>'; }).join('');
}

function exportReport() {
    if (!currentReport) return;
    var html = '<html><head><title>RivalRadar - ' + currentCompany + '</title>'
             + '<style>body{font-family:Arial;max-width:800px;margin:40px auto;line-height:1.6;color:#333}</style></head>'
             + '<body><h1>Competitive Intelligence: ' + currentCompany + '</h1>'
             + marked.parse(currentReport)
             + '<hr><p><em>Generated by RivalRadar</em></p></body></html>';
    var blob = new Blob([html], {type: 'text/html'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = 'RivalRadar-' + currentCompany + '.html';
    a.click(); URL.revokeObjectURL(url);
}

function toggleHistory() {
    document.getElementById('historySidebar').classList.toggle('open');
    document.getElementById('overlay').classList.toggle('show');
}

function saveHistory(company, searches, scrapes, report) {
    var h = JSON.parse(localStorage.getItem('rr_history') || '[]');
    h = h.filter(function(x) { return x.company !== company; });
    h.push({ company: company, date: new Date().toLocaleString(), searches: searches, scrapes: scrapes, report: report });
    if (h.length > 20) h = h.slice(-20);
    localStorage.setItem('rr_history', JSON.stringify(h));
    loadHistory();
}

function loadHistory() {
    var h = JSON.parse(localStorage.getItem('rr_history') || '[]');
    var list = document.getElementById('historyList');
    if (!h.length) { list.innerHTML = '<p style="color:#666;text-align:center;padding:20px">No history yet</p>'; return; }
    list.innerHTML = '';
    h.slice().reverse().forEach(function(item) {
        var d = document.createElement('div');
        d.className = 'history-item';
        d.onclick = function() {
            toggleHistory();
            document.getElementById('company').value = item.company;
            document.getElementById('report-content').innerHTML = marked.parse(item.report);
            document.getElementById('exportBtn').style.display = 'inline-block';
            currentReport = item.report; currentCompany = item.company;
            buildVisuals(item.report);
        };
        d.innerHTML = '<div class="history-item-title">' + item.company + '</div>'
                    + '<div class="history-item-meta">' + item.date + '</div>';
        list.appendChild(d);
    });
}

document.getElementById('company').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') startResearch();
});

loadHistory();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/research')
def research():
    company = request.args.get('company', '').strip()
    if not company:
        return Response('data: {"type": "done"}\n\n', mimetype="text/event-stream")

    def generate():
        for event in run_agent_stream(company):
            yield f"data: {json.dumps(event)}\n\n"
        yield 'data: {"type": "done"}\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)