# 🚀 ChainGuard AI

> AI-powered supply chain disruption management and fleet optimization copilot.

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | RouteX |
| **Track** | AI — L2: Supply Chain Disruption Assistant & Fleet Utilisation Optimizer |
| **Team Lead** | Yogi — [email@ibm.com] |
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

- **Feature 1** Correlates active disruptions against transit routes to identify affected freight and quantify projected delivery delays.
- **Feature 2** Evaluates operational risk scores for active shipments based on disruption severity, carrier performance, and timeline urgency.
- **Feature 3** Generates actionable rerouting and carrier reallocation suggestions to circumvent transit bottlenecks and maintain delivery SLAs.
- **Feature 4** Enables operators to simulate disruption parameters and test contingency routing strategies before committing operational changes.
- **Feature 5** Analyzes vehicle capacity and carrier availability to balance freight loads and optimize fleet resource distribution.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python |
| **Frameworks** | FastAPI |
| **IBM Technologies** | None currently integrated |
| **Databases** | PostgreSQL |
| **Other** | Docker, Git, GitHub Actions |

---

## 📁 Repository Structure

```
├── src/                  # All source code
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

> **Copy these exact steps from your [`docs/setup-guide.md`](docs/setup-guide.md)**

```bash
# 1. Clone the repo
git clone https://github.com/yogipanchal1812/bob-ai-hackathon-RouteX.git
cd bob-ai-hackathon-RouteX

# 2. Install dependencies
python -m venv .venv
# Activate environment:
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp src/.env.example src/.env
# Edit src/.env with your values

# 4. Run the project
uvicorn src.main:app --reload --port 8000
```

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
