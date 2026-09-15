# ChainGuard AI — Frontend Command Center

> Module 2 — React/Vite supply-chain command center UI.

---

## Tech Stack

| Tool | Version |
|------|---------|
| React | 18 |
| Vite | 5 |
| React Router | 6 |
| Recharts | 2 |

---

## Setup

```bash
cd src/frontend

# Install dependencies
npm install

# Copy environment config
cp .env.example .env

# Start development server (proxies /api → localhost:8000)
npm run dev

# Production build
npm run build
```

The Vite dev server runs on **http://localhost:5173** and proxies all `/api/*` requests to the backend at `http://localhost:8000`.

---

## Structure

```
src/
├── App.jsx                  # Root — BrowserRouter + Routes
├── main.jsx                 # ReactDOM entry
├── index.css                # Global design tokens + component styles
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.jsx      # Fixed sidebar navigation
│   │   └── Topbar.jsx       # Page header bar
│   └── common/
│       └── index.jsx        # Shared UI primitives
│
├── pages/
│   ├── Dashboard.jsx        # KPI cards, charts, disruption summary
│   ├── Shipments.jsx        # Shipment table + detail panel
│   ├── Disruptions.jsx      # Disruption list + impact analysis
│   ├── Fleet.jsx            # Fleet view (Member 4 API)
│   ├── WhatIf.jsx           # What-If simulator (Member 4 API)
│   └── Copilot.jsx          # AI chat panel (Member 3 API)
│
├── hooks/
│   └── useApi.js            # Generic fetch state hook
│
├── services/
│   └── api.js               # All API calls — single source of truth
│
└── utils/
    └── format.js            # Display formatting helpers (no business logic)
```

---

## API Endpoints Consumed

| Endpoint | Status |
|----------|--------|
| `GET /api/health` | ✅ Backend (Member 1) |
| `GET /api/shipments` | ✅ Backend (Member 1) |
| `GET /api/shipments/:id` | ✅ Backend (Member 1) |
| `GET /api/disruptions` | ✅ Backend (Member 1) |
| `GET /api/disruptions/:id` | ✅ Backend (Member 1) |
| `GET /api/routes` | ✅ Backend (Member 1) |
| `POST /api/analyze-disruption` | ✅ Backend (Member 1) |
| `GET /api/impact-summary` | ✅ Backend (Member 1) |
| `GET /api/fleet` | ⏳ Member 4 (ready to consume) |
| `POST /api/what-if` | ⏳ Member 4 (ready to consume) |
| `POST /api/copilot` | ⏳ Member 3 (ready to consume) |
| `POST /api/recommendation` | ⏳ Member 3 (ready to consume) |

Unavailable endpoints show graceful error states — never fake data.

---

## Engineering Rules Followed

- No backend business logic in the frontend
- No hardcoded API keys or secrets
- All IDs treated as strings
- Risk levels: `LOW / MEDIUM / HIGH / CRITICAL`
- Dates displayed from ISO 8601 values (formatting only in frontend)
- Monetary values from numeric backend fields (`cargo_value`, `estimated_impact`)
- Loading / empty / error states on every data-fetching component
- No fake success responses
