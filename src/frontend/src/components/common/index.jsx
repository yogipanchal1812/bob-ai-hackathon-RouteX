/**
 * RouteX — Shared UI primitives (upgraded enterprise design system).
 */

import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

// ── Skeleton components ───────────────────────────────────────────────────────

export function SkeletonText({ width = '100%', style }) {
  return <div className="skeleton skeleton-text" style={{ width, ...style }} />
}
export function SkeletonTitle({ width = '60%' }) {
  return <div className="skeleton skeleton-title" style={{ width }} />
}
export function SkeletonValue() {
  return <div className="skeleton skeleton-value" />
}
export function SkeletonChart() {
  return <div className="skeleton skeleton-chart" />
}
export function SkeletonRow() {
  return <div className="skeleton skeleton-row" style={{ marginBottom: 2 }} />
}

export function SkeletonKpiCard() {
  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
        <SkeletonText width="60%" />
      </div>
      <SkeletonValue />
      <SkeletonText width="50%" style={{ marginTop: 'var(--space-2)' }} />
    </div>
  )
}

export function SkeletonTable({ rows = 5, cols = 5 }) {
  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {Array(cols).fill(0).map((_, i) => (
              <th key={i}><SkeletonText width={i === 0 ? 80 : 60} /></th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array(rows).fill(0).map((_, i) => (
            <tr key={i}>
              {Array(cols).fill(0).map((__, j) => (
                <td key={j}><SkeletonText width={j === 0 ? 70 : j === cols - 1 ? 50 : 80} /></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── State views ───────────────────────────────────────────────────────────────

export function LoadingState({ message = 'Loading…' }) {
  return (
    <div className="state-view">
      <div className="loading-spinner" role="status" aria-label="Loading" />
      <p>{message}</p>
    </div>
  )
}

export function EmptyState({ title = 'No data', message = 'Nothing to display.', icon }) {
  return (
    <div className="state-view">
      {icon && <span className="state-icon" aria-hidden="true" style={{ fontSize: 24 }}>{icon}</span>}
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state-view">
      <AlertTriangle size={28} color="var(--risk-high)" />
      <h3>Something went wrong</h3>
      <p>{message || 'An unexpected error occurred.'}</p>
      {onRetry && (
        <button className="btn btn-secondary btn-sm" onClick={onRetry}>
          <RefreshCw size={12} /> Retry
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

// ── Risk / Status badges ──────────────────────────────────────────────────────

export function RiskBadge({ level, dot = false }) {
  if (!level) return <span className="badge" style={{ color: 'var(--text-muted)' }}>—</span>
  return (
    <span className={`badge badge-${level.toUpperCase()}${dot ? ' badge-dot' : ''}`}>
      {level.toUpperCase()}
    </span>
  )
}

export function StatusBadge({ status }) {
  if (!status) return <span className="badge" style={{ color: 'var(--text-muted)' }}>—</span>
  return (
    <span className={`badge badge-${status.toUpperCase()}`}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}

export function TypeBadge({ type }) {
  if (!type) return null
  return (
    <span className="badge badge-type">
      {type.replace(/_/g, ' ')}
    </span>
  )
}

// ── Risk score bar ────────────────────────────────────────────────────────────

export function RiskScoreBar({ score, level }) {
  const pct = Math.min(100, Math.max(0, score || 0))
  return (
    <div className="score-bar-wrap" title={`Risk score: ${score}`}>
      <span className="score-bar-val" style={{ color: `var(--risk-${(level || 'medium').toLowerCase()})` }}>
        {score ?? '—'}
      </span>
      <div className="score-bar-track">
        <div
          className={`score-bar-fill ${level || 'MEDIUM'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// ── Section card ──────────────────────────────────────────────────────────────

export function SectionCard({ title, children, headerExtra, style, noPad }) {
  return (
    <div className="card" style={{ padding: noPad ? 0 : undefined, overflow: noPad ? 'hidden' : undefined, ...style }}>
      {title && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 'var(--space-4)',
          padding: noPad ? 'var(--space-4) var(--space-5) 0' : undefined,
        }}>
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

// ── Currency ──────────────────────────────────────────────────────────────────

export function CurrencyDisplay({ value }) {
  if (value == null || isNaN(value)) return <span style={{ color: 'var(--text-muted)' }}>—</span>
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
  if (total === 0) return (
    <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>No affected shipments.</p>
  )
  const pct = (n) => `${((n / total) * 100).toFixed(0)}%`
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
        {medium_risk > 0 && <span style={{ color: 'var(--risk-medium)' }}>● MED {medium_risk} ({pct(medium_risk)})</span>}
        {high_risk > 0 && <span style={{ color: 'var(--risk-high)' }}>● HIGH {high_risk} ({pct(high_risk)})</span>}
        {critical_risk > 0 && <span style={{ color: 'var(--risk-critical)' }}>● CRIT {critical_risk} ({pct(critical_risk)})</span>}
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
