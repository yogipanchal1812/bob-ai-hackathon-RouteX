/**
 * Common reusable UI components for ChainGuard AI frontend.
 */

import React from 'react'
import { riskBadgeClass, statusBadgeClass, riskColor } from '../../utils/format.js'

// ── Loading state ─────────────────────────────────────────────────────────────

export function LoadingState({ message = 'Loading…' }) {
  return (
    <div className="state-view">
      <div className="loading-spinner" role="status" aria-label="Loading" />
      <p>{message}</p>
    </div>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────────

export function EmptyState({ title = 'No data', message = 'Nothing to display.', icon = '📭' }) {
  return (
    <div className="state-view">
      <span className="state-icon" aria-hidden="true">{icon}</span>
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  )
}

// ── Error state ───────────────────────────────────────────────────────────────

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state-view">
      <span className="state-icon" aria-hidden="true">⚠️</span>
      <h3>Something went wrong</h3>
      <p>{message || 'An unexpected error occurred.'}</p>
      {onRetry && (
        <button className="btn btn-secondary btn-sm" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  )
}

// ── Alert banner ──────────────────────────────────────────────────────────────

export function AlertBanner({ type = 'info', children, onClose }) {
  return (
    <div className={`alert-banner ${type}`} role="alert">
      <span>{children}</span>
      {onClose && (
        <button className="alert-close" onClick={onClose} aria-label="Dismiss">✕</button>
      )}
    </div>
  )
}

// ── Risk badge ────────────────────────────────────────────────────────────────

export function RiskBadge({ level }) {
  if (!level) return <span className="badge">—</span>
  return <span className={riskBadgeClass(level)}>{level}</span>
}

// ── Status badge ──────────────────────────────────────────────────────────────

export function StatusBadge({ status }) {
  if (!status) return <span className="badge">—</span>
  return <span className={statusBadgeClass(status)}>{status.replace(/_/g, ' ')}</span>
}

// ── Risk score bar ────────────────────────────────────────────────────────────

export function RiskScoreBar({ score, level }) {
  const pct = Math.min(100, Math.max(0, score || 0))
  return (
    <div className="score-bar-wrap">
      <span style={{ minWidth: 28, fontWeight: 700, fontSize: 'var(--text-sm)' }}>{score ?? '—'}</span>
      <div className="score-bar-track" title={`Risk score: ${score}`}>
        <div
          className={`score-bar-fill ${level || 'MEDIUM'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// ── Section card ──────────────────────────────────────────────────────────────

export function SectionCard({ title, children, headerExtra, style }) {
  return (
    <div className="card" style={style}>
      {title && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-4)' }}>
          <h2 className="section-title" style={{ margin: 0 }}>{title}</h2>
          {headerExtra && <div>{headerExtra}</div>}
        </div>
      )}
      {children}
    </div>
  )
}

// ── Detail field ──────────────────────────────────────────────────────────────

export function DetailField({ label, value, mono = false }) {
  return (
    <div className="detail-field">
      <label>{label}</label>
      <div className={`field-value${mono ? ' mono' : ''}`}>{value ?? '—'}</div>
    </div>
  )
}

// ── Currency display ──────────────────────────────────────────────────────────

export function CurrencyDisplay({ value }) {
  if (value == null || isNaN(value)) return <span>—</span>
  let display
  if (value >= 1_000_000) display = `$${(value / 1_000_000).toFixed(2)}M`
  else if (value >= 1_000) display = `$${(value / 1_000).toFixed(1)}K`
  else display = `$${Number(value).toFixed(2)}`
  return <span title={`$${Number(value).toLocaleString()}`}>{display}</span>
}

// ── Risk distribution bar ─────────────────────────────────────────────────────

export function RiskDistributionBar({ distribution }) {
  if (!distribution) return null
  const { low_risk = 0, medium_risk = 0, high_risk = 0, critical_risk = 0 } = distribution
  const total = low_risk + medium_risk + high_risk + critical_risk
  if (total === 0) return <p className="text-muted" style={{ fontSize: 'var(--text-sm)' }}>No affected shipments.</p>

  const pct = (n) => `${((n / total) * 100).toFixed(1)}%`

  return (
    <div>
      <div className="risk-dist-bar" style={{ marginBottom: 'var(--space-3)' }}>
        {low_risk > 0 && <div className="risk-dist-segment LOW" style={{ flex: low_risk }} title={`LOW: ${low_risk}`} />}
        {medium_risk > 0 && <div className="risk-dist-segment MEDIUM" style={{ flex: medium_risk }} title={`MEDIUM: ${medium_risk}`} />}
        {high_risk > 0 && <div className="risk-dist-segment HIGH" style={{ flex: high_risk }} title={`HIGH: ${high_risk}`} />}
        {critical_risk > 0 && <div className="risk-dist-segment CRITICAL" style={{ flex: critical_risk }} title={`CRITICAL: ${critical_risk}`} />}
      </div>
      <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap', fontSize: 'var(--text-xs)' }}>
        {low_risk > 0 && <span style={{ color: 'var(--risk-low)' }}>● LOW {low_risk} ({pct(low_risk)})</span>}
        {medium_risk > 0 && <span style={{ color: 'var(--risk-medium)' }}>● MEDIUM {medium_risk} ({pct(medium_risk)})</span>}
        {high_risk > 0 && <span style={{ color: 'var(--risk-high)' }}>● HIGH {high_risk} ({pct(high_risk)})</span>}
        {critical_risk > 0 && <span style={{ color: 'var(--risk-critical)' }}>● CRITICAL {critical_risk} ({pct(critical_risk)})</span>}
      </div>
    </div>
  )
}

// ── Page header ───────────────────────────────────────────────────────────────

export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="page-header page-header-row">
      <div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {actions && <div className="flex-row">{actions}</div>}
    </div>
  )
}
