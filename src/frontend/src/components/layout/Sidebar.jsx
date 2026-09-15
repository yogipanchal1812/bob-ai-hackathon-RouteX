/**
 * RouteX Frontend — Sidebar navigation
 */

import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/',            label: 'Dashboard',   icon: '⬡' },
  { to: '/disruptions', label: 'Disruptions', icon: '⚡' },
  { to: '/shipments',   label: 'Shipments',   icon: '📦' },
  { to: '/fleet',       label: 'Fleet',       icon: '🚢' },
  { to: '/what-if',     label: 'What-If',     icon: '🔬' },
  { to: '/copilot',     label: 'AI Copilot',  icon: '🤖' },
]

export default function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Main navigation">
      <div className="sidebar-logo">
        <span className="logo-mark" aria-hidden="true">⬡</span>
        <div>
          <div className="logo-name">ChainGuard AI</div>
          <div className="logo-sub">RouteX Command Center</div>
        </div>
      </div>

      <ul className="sidebar-nav" role="list">
        {NAV_ITEMS.map(({ to, label, icon }) => (
          <li key={to}>
            <NavLink
              to={to}
              end={to === '/'}
              className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
              aria-current={({ isActive }) => isActive ? 'page' : undefined}
            >
              <span className="sidebar-icon" aria-hidden="true">{icon}</span>
              <span>{label}</span>
            </NavLink>
          </li>
        ))}
      </ul>

      <div className="sidebar-footer">
        <span className="text-muted" style={{ fontSize: 'var(--text-xs)' }}>
          v1.0 · Member 2
        </span>
      </div>
    </nav>
  )
}
