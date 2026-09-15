/**
 * RouteX — Collapsible sidebar with Lucide icons, system status, nav.
 */

import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Zap, Package, Ship, FlaskConical, Bot,
  ChevronLeft, ChevronRight, Activity, Cpu, Database,
} from 'lucide-react'
import { useAppContext } from '../../context/AppContext.jsx'
import { useApi } from '../../hooks/useApi.js'
import { fetchHealth } from '../../services/api.js'

const NAV_ITEMS = [
  { to: '/',            label: 'Overview',        Icon: LayoutDashboard, end: true },
  { to: '/disruptions', label: 'Disruptions',      Icon: Zap },
  { to: '/shipments',   label: 'Shipments',         Icon: Package },
  { to: '/fleet',       label: 'Fleet',              Icon: Ship },
  { to: '/what-if',     label: 'What-If Simulator', Icon: FlaskConical },
  { to: '/copilot',     label: 'AI Copilot',        Icon: Bot },
]

export default function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppContext()
  const { data: healthData } = useApi(() => fetchHealth(), [], { immediate: true })
  const isBackendOnline = !!healthData?.status

  return (
    <nav className={`sidebar${sidebarCollapsed ? ' collapsed' : ''}`} aria-label="Main navigation">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon" aria-hidden="true">R</div>
        {!sidebarCollapsed && (
          <div className="sidebar-brand-text">
            <div className="sidebar-brand-name">RouteX</div>
            <div className="sidebar-brand-sub">Command Center</div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="sidebar-nav-section">
        {!sidebarCollapsed && (
          <div className="sidebar-nav-label">Navigation</div>
        )}
        <nav className="sidebar-nav">
          <ul role="list">
            {NAV_ITEMS.map(({ to, label, Icon, end }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  end={end}
                  className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
                  title={sidebarCollapsed ? label : undefined}
                  aria-label={label}
                >
                  <span className="sidebar-link-icon">
                    <Icon size={16} strokeWidth={1.8} />
                  </span>
                  {!sidebarCollapsed && (
                    <span className="sidebar-link-label">{label}</span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      {/* System Status */}
      <div className="sidebar-status">
        {!sidebarCollapsed && (
          <div className="sidebar-status-title">System Status</div>
        )}
        <div className="status-item" title="Backend API">
          <span className={`status-dot ${isBackendOnline ? 'online' : 'offline'}`} />
          {!sidebarCollapsed && (
            <span className="status-item-label">
              <Activity size={10} style={{ display: 'inline', marginRight: 4 }} />
              Backend {isBackendOnline ? '· Online' : '· Offline'}
            </span>
          )}
        </div>
        <div className="status-item" title="AI Engine">
          <span className="status-dot unknown" />
          {!sidebarCollapsed && (
            <span className="status-item-label">
              <Cpu size={10} style={{ display: 'inline', marginRight: 4 }} />
              AI Engine · Pending
            </span>
          )}
        </div>
        <div className="status-item" title="Data Pipeline">
          <span className={`status-dot ${isBackendOnline ? 'online' : 'unknown'}`} />
          {!sidebarCollapsed && (
            <span className="status-item-label">
              <Database size={10} style={{ display: 'inline', marginRight: 4 }} />
              Data {isBackendOnline ? '· Live' : '· Unknown'}
            </span>
          )}
        </div>
      </div>

      {/* Collapse toggle */}
      <button
        className="sidebar-collapse-btn"
        onClick={toggleSidebar}
        aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        title={sidebarCollapsed ? 'Expand' : 'Collapse'}
      >
        {sidebarCollapsed
          ? <ChevronRight size={14} />
          : <ChevronLeft size={14} />
        }
      </button>
    </nav>
  )
}
