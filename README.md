# 🎯 RivalRadar

<div align="center">

### *Know Your Competition Before They Know You*

**An autonomous AI agent that delivers deep competitive intelligence in real-time**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash_Lite-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Bright Data](https://img.shields.io/badge/Bright_Data-FF6B35?style=for-the-badge&logo=data&logoColor=white)](https://brightdata.com)
[![MCP](https://img.shields.io/badge/MCP-Enabled-8A2BE2?style=for-the-badge&logo=protocols&logoColor=white)](https://modelcontextprotocol.io)

---

> 🏆 **Built for Hackathon** — Research any company's top competitors in under 2 minutes using live web data, AI reasoning, and real-time streaming.

</div>

---

## 📸 Screenshots

> *(Add your screenshots here)*

| Agent Activity | Intelligence Report |
|:-:|:-:|
| ![activity](screenshots/activity.png) | ![report](screenshots/report.png) |

| Competitor Cards | Charts & Analysis |
|:-:|:-:|
| ![cards](screenshots/cards.png) | ![charts](screenshots/charts.png) |

---

## 🧠 What is RivalRadar?

RivalRadar is an **autonomous AI research agent** that works like a human analyst — but 100x faster. You type a company name, and the agent:

1. **Searches** Google in real-time for competitors, pricing, news, and hiring signals
2. **Scrapes** actual web pages — pricing pages, news articles, LinkedIn job listings
3. **Reasons** over collected data using Gemini 2.5 Flash Lite
4. **Generates** a structured competitive intelligence report with charts and visuals

All of this happens **live in front of you** — you can watch every search query and page scrape as it happens.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Autonomous AI Agent** | Gemini 2.5 Flash Lite decides what to search and scrape — no hardcoded logic |
| 🔍 **Live Google Search** | Real-time SERP results via Bright Data API |
| 🌐 **Deep Web Scraping** | Full page content from pricing pages, news, LinkedIn jobs |
| ⚡ **Real-time Streaming** | Watch the agent work live via Server-Sent Events |
| 📊 **Visual Dashboard** | Market share charts, funding comparison, competitor cards |
| 💪 **SWOT Analysis** | Auto-extracted strengths & weaknesses from scraped data |
| 📜 **Search History** | All reports saved locally — revisit anytime |
| 📥 **Export Report** | Download full report as HTML file |
| ⏱️ **Live Timer** | Track exactly how long the research takes |
| 🔌 **MCP Ready** | Built on Model Context Protocol architecture for extensible tool use |

---

## 🔌 Model Context Protocol (MCP) Integration

RivalRadar is built with **MCP (Model Context Protocol)** principles at its core — the open standard that enables AI models to discover and use external tools dynamically.

### What is MCP?

The **Model Context Protocol (MCP)** is an open standard introduced by Anthropic in November 2024 that gives AI models a universal way to connect to external tools, data sources, and services. Think of it as **USB-C for AI** — one protocol, any tool, any model.

> "MCP eliminates the N×M problem. Build an MCP server once, and every MCP-compatible client can use it." — [WorkOS, 2026](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026)

### How RivalRadar Uses MCP

```
┌─────────────────────────────────────────────────────────────┐
│                    RIVALRADAR MCP ARCHITECTURE               │
│                                                              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐  │
│  │   MCP Host  │◄────►│  MCP Client │◄────►│  MCP Server │  │
│  │  (Flask App)│      │  (Gemini    │      │  (Bright    │  │
│  │             │      │   Agent)    │      │   Data)     │  │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘  │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MCP TOOLS (Function Declarations)       │   │
│  │                                                      │   │
│  │  🔍 search_web(query)                                │   │
│  │     → Bright Data SERP API → Google Search Results    │   │
│  │                                                      │   │
│  │  🌐 scrape_page(url)                                 │   │
│  │     → Bright Data Scraping Browser → Full Page HTML   │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MCP RESOURCES (Data Access)             │   │
│  │                                                      │   │
│  │  📄 Organic Search Results (title, link, desc)       │   │
│  │  📄 Scraped Page Content (clean text, truncated)     │   │
│  │  📄 Competitor Intelligence Report (markdown)        │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### MCP Components in RivalRadar

| Component | Implementation | Description |
|-----------|---------------|-------------|
| **MCP Host** | Flask Web Server | The application that orchestrates the AI agent and serves the UI |
| **MCP Client** | Gemini 2.5 Flash Lite | The AI model that decides which tools to call and when |
| **MCP Server** | Bright Data APIs | External data sources exposing SERP and scraping capabilities |
| **MCP Tools** | `search_web()` & `scrape_page()` | Function declarations registered with Gemini for dynamic tool calling |
| **MCP Resources** | Search results, scraped HTML, reports | Data returned by tools that the AI reasons over |

### Why MCP Matters for RivalRadar

1. **🔌 Plug-and-Play Tools** — Adding a new data source (e.g., LinkedIn API, Crunchbase) only requires defining a new MCP tool. No changes to the agent loop.

2. **🔄 Model Agnostic** — Currently uses Gemini, but MCP architecture allows swapping to Claude, GPT-4, or any MCP-compatible model without rewriting tool logic.

3. **📡 Standardized Communication** — All tool calls use JSON-RPC 2.0 format, making debugging, logging, and extending the system trivial.

4. **🛡️ Secure by Design** — MCP's permission-based tool calling ensures the AI only accesses approved data sources.

### MCP Tool Registration

```python
# agent.py — MCP Tool Definitions
TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="search_web",
            description="Search Google for competitor intelligence",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(type=types.Type.STRING)
                },
                required=["query"]
            )
        ),
        types.FunctionDeclaration(
            name="scrape_page",
            description="Scrape full content of any webpage",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "url": types.Schema(type=types.Type.STRING)
                },
                required=["url"]
            )
        ),
    ])
]
```

### Future MCP Extensions

RivalRadar's MCP architecture makes it easy to add:
- **📧 Email alerts** — MCP server for sending competitor updates
- **📊 CRM integration** — Push leads to Salesforce/HubSpot
- **🤝 Slack/Discord** — Share reports directly to team channels
- **📈 Google Sheets** — Auto-export data to spreadsheets
- **🔔 Webhooks** — Trigger actions when new competitors emerge

---

## 🏗️ System Architecture

```
                        ┌─────────────────────────────────┐
                        │           RIVALRADAR            │
                        │                                 │
   User Input ────────► │  ┌──────────┐  ┌─────────────┐ │
  (Company Name)        │  │  Flask   │  │   SSE Live  │ │ ◄──── Browser
                        │  │  Server  │◄─│   Stream    │ │
                        │  └────┬─────┘  └─────────────┘ │
                        │       │                        │
                        │       ▼                        │
                        │  ┌──────────────────────────┐  │
                        │  │   Gemini 2.5 Flash Lite   │  │
                        │  │      AI Agent Loop        │  │
                        │  │                           │  │
                        │  │  1. Plan research         │  │
                        │  │  2. Call tools            │  │
                        │  │  3. Analyze results       │  │
                        │  │  4. Generate report       │  │
                        │  └──────────┬───────────────┘  │
                        │             │                   │
                        │      ┌──────┴──────┐            │
                        │      ▼             ▼            │
                        │  ┌────────┐  ┌──────────┐      │
                        │  │ SERP   │  │ Scraping │      │
                        │  │  API   │  │ Browser  │      │
                        │  └───┬────┘  └────┬─────┘      │
                        └──────┼────────────┼────────────┘
                               │            │
                               ▼            ▼
                          Google        Any Website
                          Search        (Live Data)
                          Results
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **Python** | Core language | 3.10+ |
| **Flask** | Web server + SSE streaming | 3.0 |
| **google-genai** | Gemini AI SDK | Latest |
| **BeautifulSoup4** | HTML parsing & cleaning | 4.x |
| **Requests** | HTTP client | 2.x |
| **python-dotenv** | Environment config | 1.x |

### AI & Data
| Technology | Purpose |
|-----------|---------|
| **Gemini 2.5 Flash Lite** | AI reasoning, tool calling, report generation |
| **Bright Data SERP API** | Live Google search results in JSON |
| **Bright Data Scraping Browser** | JavaScript-rendered page scraping |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Vanilla JS** | No framework — fast & lightweight |
| **Chart.js** | Market share & funding charts |
| **Marked.js** | Markdown → HTML rendering |
| **CSS Grid + Flexbox** | Responsive two-panel layout |
| **Server-Sent Events** | Real-time activity streaming |

---

## 🔄 How the AI Agent Works

RivalRadar uses a **ReAct-style agent loop** — the AI reasons about what information it needs, then takes actions to get it:

```
START
  │
  ▼
[THINK] "I need to find Zomato's top competitors"
  │
  ▼
[ACT] search_web("top competitors of Zomato")
  │
  ▼
[OBSERVE] Gets: Swiggy, Blinkit, Zepto, Dunzo, Magicpin
  │
  ▼
[THINK] "Now I need pricing info for each competitor"
  │
  ▼
[ACT] search_web("Swiggy pricing delivery charges 2024")
[ACT] scrape_page("https://swiggy.com/pricing")
  │
  ▼
[OBSERVE] Gets actual pricing data from live pages
  │
  ▼
[REPEAT for each competitor — news, hiring, funding]
  │
  ▼
[GENERATE] Full structured markdown report
  │
  ▼
END ✅
```

The agent autonomously decides **how many searches to do**, **which pages to scrape**, and **when it has enough data** — no hardcoded logic.

---

## 📁 Project Structure

```
rivalradar/
│
├── 🤖 agent.py              # AI agent core
│   ├── search_web()         #   → Bright Data SERP API
│   ├── scrape_page()        #   → Bright Data Scraping Browser
│   ├── run_agent_stream()   #   → Gemini agent loop (generator)
│   └── TOOLS definition     #   → MCP Function declarations for Gemini
│
├── 🌐 app_visuals.py                # Flask web server + full UI
│   ├── GET /                #   → Serve HTML dashboard
│   ├── GET /research        #   → SSE stream endpoint
│   └── HTML/CSS/JS          #   → Complete frontend (single file)
│
├── 📋 requirements.txt      # Python dependencies
├── 🚀 Procfile              # Deployment config (Railway/Render)
├── 🔐 .env                  # API keys (never commit this!)
└── 📖 README.md             # This file
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- Gemini API Key (free at [aistudio.google.com](https://aistudio.google.com/apikey))
- Bright Data Account (free $250 credits at [brightdata.com](https://brightdata.com))

### Step 1 — Clone & Install
```bash
git clone https://github.com/yourusername/rivalradar.git
cd rivalradar

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### Step 2 — Configure API Keys
Create `.env` file in project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
SERP_ZONE=serp_api2
SCRAPING_ZONE=scraping_browser1
```

### Step 3 — Bright Data Zone Setup
1. Login to [brightdata.com](https://brightdata.com)
2. Go to **Proxies & Scraping** → **Add Zone**
3. Create **SERP API** zone → name it `serp_api2`
4. Create **Scraping Browser** zone → name it `scraping_browser1`
5. Copy your API key from **Account Settings**

### Step 4 — Run
```bash
python app_visuals.py
```
Open **http://localhost:5000** 🎉

---

## 🌐 Deployment

### Railway (Recommended — Free tier)

```bash
# 1. Push to GitHub
git init && git add . && git commit -m "RivalRadar v1"
gh repo create rivalradar --public --push

# 2. Go to railway.app → New Project → Deploy from GitHub
# 3. Add environment variables in Railway dashboard
# 4. Done! Live URL auto-generated 🚀
```

### Render (Alternative — Free tier)
1. Push to GitHub
2. [render.com](https://render.com) → **New Web Service** → Connect repo
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `gunicorn app_visuals:app`
5. Add environment variables → **Deploy**

---

## 📦 Requirements

```txt
flask
requests
python-dotenv
google-genai
beautifulsoup4
gunicorn
```

---

## 🔐 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google AI Studio API key | `AIzaSy...` |
| `BRIGHT_DATA_API_KEY` | Bright Data account API key | `a4308f...` |
| `SERP_ZONE` | Bright Data SERP zone name | `serp_api2` |
| `SCRAPING_ZONE` | Bright Data Scraping Browser zone name | `scraping_browser1` |

---

## 💡 Example Use Cases

- 🍕 **Food Tech:** Research Zomato, Swiggy, Blinkit competitors
- 🛒 **E-commerce:** Analyze Flipkart, Meesho, Amazon India landscape  
- 💳 **Fintech:** Map competitors of Razorpay, PhonePe, Paytm
- 🏨 **Travel:** Intelligence on MakeMyTrip, OYO, Ixigo rivals
- 🎓 **EdTech:** Competitive analysis for BYJU'S, Unacademy, Vedantu

---

## ⚠️ Known Limitations

- Market share chart uses **estimated data** (actual market share data requires paid sources)
- Funding chart shows **relative comparison** — exact figures depend on what appears in scraped content
- Some pages may block scraping; agent falls back to search results in that case
- Gemini free tier has rate limits — large companies with many competitors may take longer

---

## 🙌 Built With Love Using

- [Google Gemini 2.5 Flash Lite](https://ai.google.dev/) — Fast, efficient AI with native tool calling
- [Bright Data](https://brightdata.com/) — Industry-leading web data infrastructure  
- [Model Context Protocol](https://modelcontextprotocol.io/) — Open standard for AI tool integration
- [Chart.js](https://www.chartjs.org/) — Beautiful, responsive charts
- [Marked.js](https://marked.js.org/) — Fast markdown parser
- [Flask](https://flask.palletsprojects.com/) — Lightweight Python web framework

---

<div align="center">

**🏆 RivalRadar — Built for Hackathon**

*From idea to working product in one session*

</div>