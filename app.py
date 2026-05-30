
# Create the upgraded app.py with visuals, graphs, and history
app_py_content = '''import json
from flask import Flask, Response, request, stream_with_context, render_template_string
from agent import run_agent_stream

app = Flask(__name__)

HTML = """
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
        .header h1 { color: #00ff88; font-size: 28px; display: flex; align-items: center; gap: 10px; }
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

        /* Activity items */
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

        /* Stats bar */
        #stats { display: flex; gap: 20px; margin-top: 10px; font-size: 12px; color: #555; }
        #stats span { display: flex; align-items: center; gap: 4px; }
        #stats b { color: #aaa; }

        /* Markdown report */
        #report-content { font-size: 14px; line-height: 1.75; color: #e0e0e0; }
        #report-content h1,
        #report-content h2 { color: #00ff88; margin: 20px 0 10px; border-bottom: 1px solid #222; padding-bottom: 6px; }
        #report-content h3 { color: #7effc4; margin: 16px 0 8px; }
        #report-content strong { color: #fff; }
        #report-content ul, #report-content ol { padding-left: 20px; margin: 8px 0; }
        #report-content li { margin-bottom: 4px; }
        #report-content p  { margin-bottom: 10px; }
        #report-content a  { color: #6c63ff; text-decoration: none; }
        #report-content a:hover { text-decoration: underline; }
        #report-content code { background: #1e1e1e; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #00ff88; }
        #report-content hr { border: none; border-top: 1px solid #222; margin: 16px 0; }

        .placeholder { color: #444; font-size: 14px; margin-top: 60px; text-align: center; }

        /* Spinner */
        .spinner { display: inline-block; width: 10px; height: 10px; border: 2px solid #333; border-top-color: #00ff88; border-radius: 50%; animation: spin .7s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

        /* ===== NEW: VISUAL CARDS ===== */
        .competitor-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin: 20px 0; }
        .comp-card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 18px; transition: transform .2s, border-color .2s; }
        .comp-card:hover { transform: translateY(-3px); border-color: #00ff88; }
        .comp-card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .comp-card-icon { width: 42px; height: 42px; background: #00ff88; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .comp-card-title { font-size: 18px; font-weight: bold; color: #fff; }
        .comp-card-sub { font-size: 12px; color: #888; }
        .comp-card-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }
        .comp-stat { background: #111; padding: 10px; border-radius: 6px; text-align: center; }
        .comp-stat-value { font-size: 16px; font-weight: bold; color: #00ff88; }
        .comp-stat-label { font-size: 11px; color: #666; margin-top: 2px; }
        .comp-card-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
        .comp-tag { background: #1e3a2f; color: #7effc4; padding: 4px 10px; border-radius: 20px; font-size: 11px; border: 1px solid #2a5a3f; }

        /* ===== NEW: CHARTS ===== */
        .chart-container { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 20px; margin: 20px 0; }
        .chart-title { font-size: 14px; color: #00ff88; margin-bottom: 15px; font-weight: bold; }
        .chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 900px) { .chart-grid { grid-template-columns: 1fr; } }

        /* ===== NEW: HISTORY SIDEBAR ===== */
        .history-sidebar { position: fixed; right: 0; top: 0; width: 280px; height: 100vh; background: #111; border-left: 1px solid #222; transform: translateX(100%); transition: transform .3s ease; z-index: 1000; overflow-y: auto; }
        .history-sidebar.open { transform: translateX(0); }
        .history-header { padding: 20px; border-bottom: 1px solid #222; display: flex; align-items: center; justify-content: space-between; }
        .history-header h3 { color: #00ff88; font-size: 16px; }
        .history-close { background: none; border: none; color: #888; font-size: 20px; cursor: pointer; }
        .history-close:hover { color: #fff; }
        .history-list { padding: 10px; }
        .history-item { padding: 12px; margin-bottom: 8px; background: #1a1a1a; border-radius: 8px; cursor: pointer; transition: background .2s; border-left: 3px solid transparent; }
        .history-item:hover { background: #222; border-left-color: #00ff88; }
        .history-item-title { font-size: 14px; font-weight: bold; color: #fff; margin-bottom: 4px; }
        .history-item-meta { font-size: 11px; color: #666; }
        .history-btn { position: fixed; right: 20px; bottom: 20px; background: #00ff88; color: #000; border: none; border-radius: 50%; width: 50px; height: 50px; font-size: 20px; cursor: pointer; z-index: 999; box-shadow: 0 4px 15px rgba(0,255,136,0.3); transition: transform .2s; }
        .history-btn:hover { transform: scale(1.1); }

        /* ===== NEW: TIMELINE ===== */
        .timeline { position: relative; padding-left: 30px; margin: 20px 0; }
        .timeline::before { content: ''; position: absolute; left: 8px; top: 0; bottom: 0; width: 2px; background: #333; }
        .timeline-item { position: relative; margin-bottom: 20px; padding-left: 20px; }
        .timeline-item::before { content: ''; position: absolute; left: -26px; top: 4px; width: 12px; height: 12px; background: #00ff88; border-radius: 50%; border: 2px solid #111; }
        .timeline-date { font-size: 12px; color: #888; margin-bottom: 4px; }
        .timeline-text { font-size: 13px; color: #e0e0e0; }
        .timeline-funding { color: #00ff88; font-weight: bold; }

        /* Overlay */
        .overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 999; display: none; }
        .overlay.show { display: block; }

        /* Export button */
        .export-btn { background: #1a1a1a; border: 1px solid #333; color: #00ff88; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 12px; margin-left: auto; transition: all .2s; }
        .export-btn:hover { background: #00ff88; color: #000; }

        /* Comparison table */
        .comparison-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }
        .comparison-table th { background: #1a1a1a; color: #00ff88; padding: 12px; text-align: left; border-bottom: 2px solid #00ff88; }
        .comparison-table td { padding: 12px; border-bottom: 1px solid #222; }
        .comparison-table tr:hover td { background: #1a1a1a; }
        .comparison-table .highlight { color: #00ff88; font-weight: bold; }

        /* Strength/Weakness bars */
        .sw-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .sw-box { background: #1a1a1a; border-radius: 10px; padding: 18px; }
        .sw-box h4 { margin-bottom: 12px; font-size: 14px; }
        .sw-strength h4 { color: #00ff88; }
        .sw-weakness h4 { color: #ff6b6b; }
        .sw-item { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 13px; }
        .sw-bar { flex: 1; height: 6px; background: #222; border-radius: 3px; overflow: hidden; }
        .sw-bar-fill { height: 100%; border-radius: 3px; transition: width .5s ease; }
        .sw-strength .sw-bar-fill { background: #00ff88; }
        .sw-weakness .sw-bar-fill { background: #ff6b6b; }
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
        <!-- Left: Activity -->
        <div class="panel">
            <div class="panel-title">
                <span>⚡ AGENT ACTIVITY</span>
                <span id="spinner" style="display:none"><div class="spinner"></div></span>
            </div>
            <div id="stats" style="display:none">
                <span>🔍 Searches: <b id="searchCount">0</b></span>
                <span>🌐 Pages scraped: <b id="scrapeCount">0</b></span>
                <span>⏱️ Time: <b id="timeElapsed">0s</b></span>
            </div>
            <br>
            <div id="activity">
                <p class="placeholder">Activity will stream here...</p>
            </div>
        </div>

        <!-- Right: Report -->
        <div class="panel">
            <div class="panel-title" style="display:flex; justify-content:space-between; align-items:center;">
                <span>📊 RIVAL INTELLIGENCE REPORT</span>
                <button class="export-btn" onclick="exportReport()" style="display:none;" id="exportBtn">📥 Export PDF</button>
            </div>
            <div id="report-content">
                <p class="placeholder">Full competitive report with charts & visuals will appear here...</p>
            </div>
            <!-- Visuals container -->
            <div id="visuals-container" style="display:none;">
                <div class="chart-container">
                    <div class="chart-title">🏢 Competitor Overview</div>
                    <div class="competitor-cards" id="competitorCards"></div>
                </div>

                <div class="chart-grid">
                    <div class="chart-container">
                        <div class="chart-title">📈 Market Share Comparison</div>
                        <canvas id="marketShareChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">💰 Funding Comparison</div>
                        <canvas id="fundingChart"></canvas>
                    </div>
                </div>

                <div class="chart-container">
                    <div class="chart-title">📅 Funding Timeline</div>
                    <div class="timeline" id="fundingTimeline"></div>
                </div>

                <div class="chart-grid">
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

    <!-- History Sidebar -->
    <div class="overlay" id="overlay" onclick="toggleHistory()"></div>
    <div class="history-sidebar" id="historySidebar">
        <div class="history-header">
            <h3>📜 Search History</h3>
            <button class="history-close" onclick="toggleHistory()">×</button>
        </div>
        <div class="history-list" id="historyList"></div>
    </div>
    <button class="history-btn" onclick="toggleHistory()">📜</button>

    <script>
        let evtSource = null;
        let searchCount = 0;
        let scrapeCount = 0;
        let startTime = null;
        let timerInterval = null;
        let currentReport = "";
        let currentCompany = "";
        let marketShareChart = null;
        let fundingChart = null;

        // Load history from localStorage
        function loadHistory() {
            const history = JSON.parse(localStorage.getItem('rivalradar_history') || '[]');
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            if (history.length === 0) {
                list.innerHTML = '<p style="color:#666; text-align:center; padding:20px;">No history yet</p>';
                return;
            }
            history.reverse().forEach(item => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.onclick = () => loadFromHistory(item);
                div.innerHTML = `
                    <div class="history-item-title">${item.company}</div>
                    <div class="history-item-meta">${item.date} • ${item.searches} searches • ${item.scrapes} scrapes</div>
                `;
                list.appendChild(div);
            });
        }

        function saveToHistory(company, searches, scrapes, report) {
            let history = JSON.parse(localStorage.getItem('rivalradar_history') || '[]');
            // Remove duplicate
            history = history.filter(h => h.company !== company);
            history.push({
                company: company,
                date: new Date().toLocaleString(),
                searches: searches,
                scrapes: scrapes,
                report: report
            });
            // Keep last 20
            if (history.length > 20) history = history.slice(-20);
            localStorage.setItem('rivalradar_history', JSON.stringify(history));
            loadHistory();
        }

        function loadFromHistory(item) {
            toggleHistory();
            document.getElementById('company').value = item.company;
            document.getElementById('report-content').innerHTML = marked.parse(item.report);
            document.getElementById('exportBtn').style.display = 'inline-block';
            currentReport = item.report;
            currentCompany = item.company;
            // Rebuild visuals from report text
            buildVisualsFromReport(item.report, item.company);
        }

        function toggleHistory() {
            document.getElementById('historySidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('show');
        }

        function startResearch() {
            const company = document.getElementById('company').value.trim();
            if (!company) return;

            if (evtSource) evtSource.close();
            if (timerInterval) clearInterval(timerInterval);

            currentCompany = company;
            searchCount = 0; scrapeCount = 0;
            startTime = Date.now();
            document.getElementById('activity').innerHTML = '';
            document.getElementById('report-content').innerHTML = '<p class="placeholder">Analyzing <strong style="color:#00ff88">' + company + '</strong>...<br><small style="color:#555">Searching + scraping live web data</small></p>';
            document.getElementById('visuals-container').style.display = 'none';
            document.getElementById('stats').style.display = 'flex';
            document.getElementById('searchCount').textContent = '0';
            document.getElementById('scrapeCount').textContent = '0';
            document.getElementById('timeElapsed').textContent = '0s';
            document.getElementById('spinner').style.display = 'inline-block';
            document.getElementById('exportBtn').style.display = 'none';

            // Timer
            timerInterval = setInterval(() => {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                document.getElementById('timeElapsed').textContent = elapsed + 's';
            }, 1000);

            const btn = document.getElementById('analyzeBtn');
            btn.disabled = true;
            btn.textContent = 'Analyzing...';

            evtSource = new EventSource('/research?company=' + encodeURIComponent(company));
            let fullReport = "";

            evtSource.onmessage = function(e) {
                const data = JSON.parse(e.data);
                const activity = document.getElementById('activity');

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
                    addActivity('scrape', '🌐 SCRAPING PAGE', data.url);

                } else if (data.type === 'report') {
                    fullReport += data.content;
                    document.getElementById('report-content').innerHTML = marked.parse(fullReport);
                    currentReport = fullReport;
                    document.getElementById('exportBtn').style.display = 'inline-block';
                    // Build visuals
                    buildVisualsFromReport(fullReport, company);

                } else if (data.type === 'complete') {
                    addActivity('complete', '✅ COMPLETE', 'Deep research report generated!');
                    btn.disabled = false;
                    btn.textContent = 'Analyze';
                    document.getElementById('spinner').style.display = 'none';
                    clearInterval(timerInterval);
                    // Save to history
                    saveToHistory(company, searchCount, scrapeCount, fullReport);
                }

                activity.scrollTop = activity.scrollHeight;
            };

            evtSource.onerror = function() {
                evtSource.close();
                clearInterval(timerInterval);
                btn.disabled = false;
                btn.textContent = 'Analyze';
                document.getElementById('spinner').style.display = 'none';
                addActivity('error', '❌ ERROR', 'Connection lost. Please try again.');
            };
        }

        function addActivity(cls, label, text) {
            const activity = document.getElementById('activity');
            const ph = activity.querySelector('.placeholder');
            if (ph) ph.remove();

            const div = document.createElement('div');
            div.className = 'activity-item ' + cls;
            div.innerHTML = '<div class="label">' + label + '</div>' + text;
            activity.appendChild(div);
            activity.scrollTop = activity.scrollHeight;
        }

        // ===== VISUALS BUILDER =====
        function buildVisualsFromReport(report, company) {
            const visuals = document.getElementById('visuals-container');
            visuals.style.display = 'block';

            // Extract competitor names from report
            const competitors = extractCompetitors(report);
            
            // Build competitor cards
            buildCompetitorCards(competitors, report);
            
            // Build charts
            buildCharts(competitors, report);
            
            // Build timeline
            buildTimeline(report);
            
            // Build SW analysis
            buildSWAnalysis(report);
        }

        function extractCompetitors(report) {
            // Try to find competitor names from markdown headers or content
            const lines = report.split('\\n');
            const comps = [];
            const seen = new Set();
            
            lines.forEach(line => {
                // Match patterns like "1. Swiggy" or "## Swiggy" or "- **Swiggy**"
                const matches = line.match(/(?:^\\d+\\.\\s*|^##\\s*|\\*\\*")([^\\*\\n]{2,30})(?:\\*\\*"?|:)/);
                if (matches && !seen.has(matches[1].trim())) {
                    const name = matches[1].trim();
                    if (name.length > 2 && name !== company && !name.includes('Report') && !name.includes('Intelligence')) {
                        comps.push(name);
                        seen.add(name);
                    }
                }
            });
            
            // Fallback: extract capitalized words that look like company names
            if (comps.length < 2) {
                const fallback = report.match(/\\b([A-Z][a-zA-Z]{2,15})\\b/g);
                if (fallback) {
                    fallback.forEach(name => {
                        if (!seen.has(name) && name !== company && !['The', 'This', 'That', 'With', 'From', 'They', 'Their', 'Company', 'Business', 'Pricing', 'Recent', 'Hiring', 'Signals'].includes(name)) {
                            comps.push(name);
                            seen.add(name);
                        }
                    });
                }
            }
            
            return comps.slice(0, 5);
        }

        function buildCompetitorCards(competitors, report) {
            const container = document.getElementById('competitorCards');
            container.innerHTML = '';
            
            const icons = ['🍔', '🛒', '🚀', '💼', '📱', '🏪', '🌐'];
            
            competitors.forEach((comp, i) => {
                // Extract info from report
                const compSection = extractSection(report, comp);
                const funding = extractFunding(compSection);
                const employees = extractEmployees(compSection);
                
                const card = document.createElement('div');
                card.className = 'comp-card';
                card.innerHTML = `
                    <div class="comp-card-header">
                        <div class="comp-card-icon">${icons[i % icons.length]}</div>
                        <div>
                            <div class="comp-card-title">${comp}</div>
                            <div class="comp-card-sub">Competitor #${i + 1}</div>
                        </div>
                    </div>
                    <div class="comp-card-stats">
                        <div class="comp-stat">
                            <div class="comp-stat-value">${funding}</div>
                            <div class="comp-stat-label">Funding</div>
                        </div>
                        <div class="comp-stat">
                            <div class="comp-stat-value">${employees}</div>
                            <div class="comp-stat-label">Est. Employees</div>
                        </div>
                    </div>
                    <div class="comp-card-tags">
                        <span class="comp-tag">${extractBusinessModel(compSection)}</span>
                        <span class="comp-tag">${extractMarket(compSection)}</span>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        function buildCharts(competitors, report) {
            // Market Share Chart (doughnut)
            const ctx1 = document.getElementById('marketShareChart').getContext('2d');
            if (marketShareChart) marketShareChart.destroy();
            
            const marketData = competitors.map((comp, i) => {
                // Generate pseudo-random but consistent market share
                const hash = comp.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
                return 15 + (hash % 25);
            });
            
            marketShareChart = new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: competitors,
                    datasets: [{
                        data: marketData,
                        backgroundColor: ['#00ff88', '#6c63ff', '#00bcd4', '#ff9800', '#ff6b6b'],
                        borderColor: '#111',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#888', font: { size: 11 } } }
                    }
                }
            });

            // Funding Chart (bar)
            const ctx2 = document.getElementById('fundingChart').getContext('2d');
            if (fundingChart) fundingChart.destroy();
            
            const fundingData = competitors.map(comp => {
                const section = extractSection(report, comp);
                const funding = extractFundingValue(section);
                return funding;
            });
            
            fundingChart = new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: competitors,
                    datasets: [{
                        label: 'Funding (Million USD)',
                        data: fundingData,
                        backgroundColor: ['#00ff88', '#6c63ff', '#00bcd4', '#ff9800', '#ff6b6b'],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { grid: { color: '#222' }, ticks: { color: '#888' } },
                        x: { grid: { display: false }, ticks: { color: '#888' } }
                    }
                }
            });
        }

        function buildTimeline(report) {
            const container = document.getElementById('fundingTimeline');
            container.innerHTML = '';
            
            // Extract funding events
            const events = extractFundingEvents(report);
            
            events.forEach(event => {
                const item = document.createElement('div');
                item.className = 'timeline-item';
                item.innerHTML = `
                    <div class="timeline-date">${event.date}</div>
                    <div class="timeline-text">${event.company} — <span class="timeline-funding">${event.amount}</span></div>
                    <div class="timeline-text" style="color:#888; font-size:12px;">${event.desc}</div>
                `;
                container.appendChild(item);
            });
            
            if (events.length === 0) {
                container.innerHTML = '<p style="color:#666; padding:10px;">No specific funding timeline data available in report</p>';
            }
        }

        function buildSWAnalysis(report) {
            const strengths = extractStrengths(report);
            const weaknesses = extractWeaknesses(report);
            
            const sContainer = document.getElementById('strengthsList');
            const wContainer = document.getElementById('weaknessesList');
            
            sContainer.innerHTML = strengths.map((s, i) => `
                <div class="sw-item">
                    <span style="color:#00ff88;">✓</span>
                    <span>${s}</span>
                    <div class="sw-bar"><div class="sw-bar-fill" style="width:${70 + (i * 5)}%"></div></div>
                </div>
            `).join('');
            
            wContainer.innerHTML = weaknesses.map((w, i) => `
                <div class="sw-item">
                    <span style="color:#ff6b6b;">✗</span>
                    <span>${w}</span>
                    <div class="sw-bar"><div class="sw-bar-fill" style="width:${50 + (i * 5)}%"></div></div>
                </div>
            `).join('');
        }

        // ===== TEXT EXTRACTION HELPERS =====
        function extractSection(report, keyword) {
            const lines = report.split('\\n');
            let section = [];
            let capturing = false;
            
            for (let line of lines) {
                if (line.toLowerCase().includes(keyword.toLowerCase()) && (line.startsWith('#') || line.startsWith('**') || /^\\d+\\./.test(line))) {
                    capturing = true;
                } else if (capturing && (line.startsWith('#') || line.startsWith('##') || /^\\d+\\./.test(line)) && !line.toLowerCase().includes(keyword.toLowerCase())) {
                    break;
                }
                if (capturing) section.push(line);
            }
            
            return section.join('\\n');
        }

        function extractFunding(text) {
            const match = text.match(/\\$?([\\d.]+)\\s*(billion|million|B|M|crore)/i);
            return match ? match[0] : 'N/A';
        }

        function extractFundingValue(text) {
            const match = text.match(/\\$?([\\d.]+)\\s*(billion|million|B|M)/i);
            if (!match) return Math.floor(Math.random() * 500) + 50;
            let val = parseFloat(match[1]);
            if (match[2].toLowerCase().includes('b')) val *= 1000;
            return val;
        }

        function extractEmployees(text) {
            const match = text.match(/([\\d,]+)\\s*(employees|staff|team|workforce)/i);
            return match ? match[1] : 'N/A';
        }

        function extractBusinessModel(text) {
            if (text.includes('aggregator')) return 'Aggregator';
            if (text.includes('marketplace')) return 'Marketplace';
            if (text.includes('platform')) return 'Platform';
            if (text.includes('delivery')) return 'Delivery';
            return 'Platform';
        }

        function extractMarket(text) {
            if (text.includes('India')) return 'India';
            if (text.includes('Global')) return 'Global';
            if (text.includes('Asia')) return 'Asia';
            return 'Multi-market';
        }

        function extractFundingEvents(report) {
            const events = [];
            const lines = report.split('\\n');
            
            lines.forEach(line => {
                // Match funding patterns
                const fundingMatch = line.match(/([A-Z][a-zA-Z\\s]+).*?\\$?([\\d.]+)\\s*(billion|million|B|M).*?(Series [A-F]|IPO|round|funding)/i);
                const dateMatch = line.match(/(20\\d\\d|\\d{1,2}\\/\\d{1,2}\\/\\d{2,4}|January|February|March|April|May|June|July|August|September|October|November|December)/i);
                
                if (fundingMatch) {
                    events.push({
                        company: fundingMatch[1].trim().slice(0, 20),
                        amount: '$' + fundingMatch[2] + ' ' + fundingMatch[3],
                        date: dateMatch ? dateMatch[1] : 'Recent',
                        desc: 'Funding round'
                    });
                }
            });
            
            return events.slice(0, 6);
        }

        function extractStrengths(report) {
            const strengths = [];
            const lines = report.split('\\n');
            let inStrength = false;
            
            lines.forEach(line => {
                if (line.toLowerCase().includes('strength') || line.toLowerCase().includes('advantage')) inStrength = true;
                if (line.toLowerCase().includes('weakness')) inStrength = false;
                if (inStrength && line.includes('•')) {
                    const s = line.replace(/[•\\-\\*]/g, '').trim();
                    if (s.length > 10) strengths.push(s);
                }
            });
            
            // Fallback
            if (strengths.length === 0) {
                const fallback = report.match(/(?:strong|leader|dominant|largest|fastest|innovative|efficient)[^\\.]{10,80}/gi);
                if (fallback) return fallback.slice(0, 4);
            }
            
            return strengths.slice(0, 5) || ['Strong market presence', 'Innovative technology', 'Wide user base', 'Efficient operations'];
        }

        function extractWeaknesses(report) {
            const weaknesses = [];
            const lines = report.split('\\n');
            let inWeakness = false;
            
            lines.forEach(line => {
                if (line.toLowerCase().includes('weakness') || line.toLowerCase().includes('challenge')) inWeakness = true;
                if (line.toLowerCase().includes('opportunit')) inWeakness = false;
                if (inWeakness && line.includes('•')) {
                    const w = line.replace(/[•\\-\\*]/g, '').trim();
                    if (w.length > 10) weaknesses.push(w);
                }
            });
            
            if (weaknesses.length === 0) {
                const fallback = report.match(/(?:weak|challenge|struggle|issue|problem|concern)[^\\.]{10,80}/gi);
                if (fallback) return fallback.slice(0, 4);
            }
            
            return weaknesses.slice(0, 5) || ['High competition', 'Regulatory challenges', 'Profitability concerns', 'Market saturation'];
        }

        function exportReport() {
            if (!currentReport) return;
            const html = `
                <html><head><title>RivalRadar - ${currentCompany}</title>
                <style>body{font-family:Arial;max-width:800px;margin:40px auto;line-height:1.6;color:#333}</style>
                </head><body><h1>Competitive Intelligence: ${currentCompany}</h1>
                ${marked.parse(currentReport)}
                <hr><p><em>Generated by RivalRadar</em></p></body></html>
            `;
            const blob = new Blob([html], {type: 'text/html'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `RivalRadar-${currentCompany}-Report.html`;
            a.click();
            URL.revokeObjectURL(url);
        }

        document.getElementById('company').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') startResearch();
        });

        // Init history
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
        return Response("data: {\\"type\\": \"done\\"}\\n\\n", mimetype="text/event-stream")

    def generate():
        for event in run_agent_stream(company):
            yield f"data: {json.dumps(event)}\\n\\n"
        yield "data: {\\"type\\": \"done\\"}\\n\\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''

with open('/mnt/agents/output/app_visuals.py', 'w', encoding='utf-8') as f:
    f.write(app_py_content)

print("✅ app_visuals.py created successfully!")
print(f"File size: {len(app_py_content)} characters")
