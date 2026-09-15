/**
 * RouteX — Professional top bar with system status, last updated, page info.
 */

import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { RefreshCw } from 'lucide-react'

const PAGE_META = {
  '/':            { title: 'Supply Chain Command Center', sub: 'Real-time disruption intelligence and operational risk overview' },
  '/disruptions': { title: 'Disruption Intelligence',    sub: 'Monitor active disruption events and assess operational exposure' },
  '/shipments':   { title: 'Shipment Operations',        sub: 'Track, filter and analyze active cargo shipments' },
  '/fleet':       { title: 'Fleet Operations',           sub: 'Vehicle capacity, availability, and utilization' },
  '/what-if':     { title: 'What-If Simulator',          sub: 'Simulate disruption scenarios and evaluate operational consequences' },
  '/copilot':     { title: 'RouteX AI Copilot',          sub: 'AI-powered decision support for supply chain operations' },
}

function LiveClock() {
  const [time, setTime] = useState(() => new Date().toLocaleTimeString('en-US', { hour12: false }))
  useEffect(() => {
    const id = setInterval(() => {
      setTime(new Date().toLocaleTimeString('en-US', { hour12: false }))
    }, 1000)
    return () => clearInterval(id)
  }, [])
  return <span className="topbar-updated">{time}</span>
}

export default function Topbar() {
  const { pathname } = useLocation()
  const meta = PAGE_META[pathname] || { title: 'RouteX', sub: '' }

  return (
    <header className="topbar" role="banner">
      <div className="topbar-left">
        <div className="topbar-title">{meta.title}</div>
        {meta.sub && <div className="topbar-sub">{meta.sub}</div>}
      </div>

      <div className="topbar-right">
        <div className="topbar-status-group">
          <div className="topbar-status-item">
            <span className="status-dot online" />
            <span>SYSTEM OPERATIONAL</span>
          </div>
          <div className="topbar-sep" />
          <div className="topbar-status-item">
            <RefreshCw size={10} />
            <LiveClock />
          </div>
        </div>
      </div>
    </header>
  )
}
