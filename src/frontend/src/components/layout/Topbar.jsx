/**
 * RouteX Frontend — Top bar
 */

import React from 'react'
import { useLocation } from 'react-router-dom'

const PAGE_TITLES = {
  '/':            'Dashboard',
  '/disruptions': 'Disruptions',
  '/shipments':   'Shipments',
  '/fleet':       'Fleet',
  '/what-if':     'What-If Simulator',
  '/copilot':     'AI Copilot',
}

export default function Topbar() {
  const { pathname } = useLocation()
  const title = PAGE_TITLES[pathname] || 'ChainGuard AI'

  return (
    <header className="topbar">
      <span className="topbar-title">{title}</span>
      <div className="topbar-right">
        <span className="topbar-badge" title="Backend API">
          <span className="status-dot" aria-hidden="true" />
          API
        </span>
      </div>
    </header>
  )
}
