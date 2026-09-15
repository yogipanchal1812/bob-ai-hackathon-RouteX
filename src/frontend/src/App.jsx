/**
 * RouteX Frontend — App root with routing, context, and toast system.
 */

import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { AppProvider, useAppContext } from './context/AppContext.jsx'
import Sidebar from './components/layout/Sidebar.jsx'
import Topbar from './components/layout/Topbar.jsx'
import ToastContainer from './components/common/ToastContainer.jsx'

import Dashboard from './pages/Dashboard.jsx'
import Disruptions from './pages/Disruptions.jsx'
import Shipments from './pages/Shipments.jsx'
import Fleet from './pages/Fleet.jsx'
import WhatIf from './pages/WhatIf.jsx'
import Copilot from './pages/Copilot.jsx'

function Shell() {
  const { sidebarCollapsed } = useAppContext()
  return (
    <div className="app-shell">
      <Sidebar />
      <div className={`main-content${sidebarCollapsed ? ' sidebar-collapsed' : ''}`}>
        <Topbar />
        <main className="page-body page-enter">
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
      <ToastContainer />
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <Shell />
      </AppProvider>
    </BrowserRouter>
  )
}
