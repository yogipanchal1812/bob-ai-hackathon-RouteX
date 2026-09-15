# 🚀 ChainGuard AI

> AI-powered supply chain disruption management and fleet optimization copilot.

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | RouteX |
| **Track** | AI — L2: Supply Chain Disruption Assistant & Fleet Utilisation Optimizer |
| **Team Lead** | Yogi — 24dce082@charusat.edu.in |
| **Members** | Prapti, Tirth, Ridhhi |

---

## 🎯 Problem Statement

> In 2–3 sentences: What problem does your project solve? Who experiences this problem?

Supply chain managers face constant operational uncertainty when unexpected disruptions, such as severe weather, port congestion, or route closures, strike active transportation networks. Without unified real-time visibility, identifying affected shipments and quantifying the associated delay and financial risks becomes slow and complex. Consequently, operations teams struggle to make rapid, optimal decisions regarding alternative route selection, carrier reallocation, and fleet utilization to mitigate costly bottlenecks.

---

## 💡 Solution

> In 2–3 sentences: What did you build? How does it solve the problem above?

ChainGuard AI is an intelligent disruption assistant and fleet utilization optimizer designed to streamline operational response. The platform analyzes disruption data alongside active shipment schedules, route corridors, carrier metrics, and vehicle capacity to identify impacted cargo and evaluate risk severity. By delivering actionable rerouting recommendations and supporting what-if scenario simulations, ChainGuard AI empowers logistics coordinators to optimize fleet resources and execute timely mitigation plans.


---

## ✨ Key Features

- **Disruption Impact Analysis:** Correlates active disruptions against transit routes to identify affected freight and quantify projected delivery delays.
- **Shipment Risk Assessment:** Evaluates operational risk scores for active shipments based on disruption severity, carrier performance, and timeline urgency.
- **AI-Driven Recommendations:** Generates actionable rerouting and carrier reallocation suggestions to circumvent transit bottlenecks and maintain delivery SLAs.
- **What-If Scenario Simulation:** Enables operators to simulate disruption parameters and test contingency routing strategies before committing operational changes.
- **Fleet Utilization Optimization:** Analyzes vehicle capacity and carrier availability to balance freight loads and optimize fleet resource distribution.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python, JavaScript (ES6+) |
| **Frameworks** | FastAPI, React 18, Vite |
| **IBM Technologies** | watsonx.ai (in progress) |
| **Databases** | In-Memory / CSV Data Store |
| **Other** | Recharts, Docker, Git, GitHub Actions |

---

## 📁 Repository Structure

```
├── src/
│   ├── backend/          # FastAPI Disruption & Risk Intelligence Engine
│   └── frontend/         # React + Vite Operations Dashboard
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt  # Link to demo video
├── presentation/         # Slide deck
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/yogipanchal1812/bob-ai-hackathon-RouteX.git
cd bob-ai-hackathon-RouteX
```

### 2. Backend Setup & Run (Member 1)
```bash
cd src/backend

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automated test suite (41 tests)
pytest tests/ -v

# Start FastAPI backend server (http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup & Run (Member 2)
In a new terminal window:
```bash
cd src/frontend

# Install dependencies
npm install

# Start Vite development server (http://localhost:5173)
npm run dev
```

The application will be accessible at:
* **Frontend UI:** `http://localhost:5173`
* **Backend API & Swagger Docs:** `http://localhost:8000/docs`

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.pdf](presentation/) |

---

## ⚠️ Known Limitations

> Be honest — judges appreciate transparency over overclaiming.

- **Simulated Disruption Scenarios:** Disruption events and corridor bottlenecks are currently evaluated using curated simulation datasets rather than live global telematics and IoT streaming feeds.
- **Limited Carrier & Fleet Telematics:** Fleet capacity and carrier metrics are modeled using representative benchmark data rather than direct enterprise ERP/TMS integrations.
- **Local Prototype Scope:** The application is configured and verified for local development execution, with containerized multi-tenant cloud deployment planned for future releases.

---

## 🏅 What We're Most Proud Of

We are most proud of designing ChainGuard AI to address an urgent, high-friction operational challenge in supply chain management: translating complex, unstructured disruption events into immediate, actionable operational decisions. Rather than presenting static alerts or dashboards, ChainGuard AI bridges data analytics with AI-assisted decision support, enabling logistics operators to swiftly identify affected shipments, simulate what-if rerouting scenarios, and reallocate fleet capacity in minutes. By focusing on practical decision support tailored directly for real-world supply chain coordinators, RouteX delivers a functional solution that transforms reactive firefighting into proactive disruption response.

---
