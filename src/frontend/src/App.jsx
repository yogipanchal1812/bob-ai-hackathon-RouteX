/**
 * RouteX Frontend — App root with routing.
 */

import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Sidebar from './components/layout/Sidebar.jsx'
import Topbar from './components/layout/Topbar.jsx'

import Dashboard from './pages/Dashboard.jsx'
import Disruptions from './pages/Disruptions.jsx'
import Shipments from './pages/Shipments.jsx'
import Fleet from './pages/Fleet.jsx'
import WhatIf from './pages/WhatIf.jsx'
import Copilot from './pages/Copilot.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <div className="main-content">
          <Topbar />
          <main className="page-body">
            <Routes>
              <Route path="/"            element={<Dashboard />} />
              <Route path="/disruptions" element={<Disruptions />} />
              <Route path="/shipments"   element={<Shipments />} />
              <Route path="/fleet"       element={<Fleet />} />
              <Route path="/what-if"     element={<WhatIf />} />
              <Route path="/copilot"     element={<Copilot />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
