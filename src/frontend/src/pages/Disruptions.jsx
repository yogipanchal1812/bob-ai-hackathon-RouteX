/**
 * RouteX — Disruptions: Disruption Intelligence page with filter chips, analysis, drawer.
 *
 * Consumes: GET /api/disruptions, POST /api/analyze-disruption
 */

import React, { useState, useMemo, useCallback } from 'react'
import { Search, Filter, Zap, X } from 'lucide-react'

import { useApi, useApiMutation } from '../hooks/useApi.js'
import { fetchDisruptions, analyzeDisruption } from '../services/api.js'
import {
  SkeletonTable, ErrorState, EmptyState, SectionCard, AlertBanner,
  RiskBadge, StatusBadge, CurrencyDisplay, RiskScoreBar, RiskDistributionBar, TypeBadge,
} from '../components/common/index.jsx'
import Drawer from '../components/common/Drawer.jsx'
import { formatDisruptionType } from '../utils/format.js'
import { useAppContext } from '../context/AppContext.jsx'

const SEVERITY_FILTERS = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
const STATUS_FILTERS   = ['ALL', 'ACTIVE', 'MONITORING', 'RESOLVED']

export default function Disruptions() {
  const { addToast } = useAppContext()
  const [statusFilter, setStatusFilter] = useState('ACTIVE')
  const [severityFilter, setSeverityFilter] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [drawerDisruption, setDrawerDisruption] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)

  // ── Fetch list ────────────────────────────────────────────────────────────────
  const { data, loading, error, refetch } = useApi(
    () => fetchDisruptions(statusFilter !== 'ALL' ? { status: statusFilter } : {}),
    [statusFilter]
  )
  const disruptions = data?.data || []

  // ── Filter client-side by severity + search ─────────────────────────────────
  const filtered = useMemo(() => {
    let list = disruptions
    if (severityFilter !== 'ALL') list = list.filter(d => d.severity === severityFilter)
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      list = list.filter(d =>
        d.location.toLowerCase().includes(q) ||
        d.type.toLowerCase().includes(q) ||
        d.disruption_id.toLowerCase().includes(q) ||
        d.description?.toLowerCase().includes(q)
      )
    }
    return list
  }, [disruptions, severityFilter, searchQuery])

  // ── Analyze mutation ──────────────────────────────────────────────────────────
  const { loading: analyzing, execute: runAnalysis } = useApiMutation(analyzeDisruption)

  const handleAnalyze = useCallback(async (disruption) => {
    setDrawerDisruption(disruption)
    setAnalysisResult(null)
    try {
      const result = await runAnalysis(disruption.disruption_id)
      setAnalysisResult(result?.data || result)
      addToast(`Analysis complete for ${disruption.disruption_id}`, 'success')
    } catch (err) {
      addToast(`Analysis failed: ${err.message}`, 'error')
    }
  }, [runAnalysis, addToast])

  const closeDrawer = () => {
    setDrawerDisruption(null)
    setAnalysisResult(null)
  }

  return (
    <div>
      {/* ── Controls row ──────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 'var(--space-3)', marginBottom: 'var(--space-5)', flexWrap: 'wrap', alignItems: 'center' }}>
        {/* Search */}
        <div className="search-box" style={{ flex: '1 1 220px', maxWidth: 320 }}>
          <span className="search-box-icon"><Search size={13} /></span>
          <input
            type="search"
            placeholder="Search location, type, ID…"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            aria-label="Search disruptions"
          />
        </div>

        {/* Status chips */}
        <div className="filter-row" style={{ margin: 0 }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginRight: 4 }}>
            <Filter size={11} style={{ display: 'inline' }} /> Status:
          </span>
          {STATUS_FILTERS.map(s => (
            <button
              key={s}
              className={`filter-chip${statusFilter === s ? ' active' : ''}`}
              onClick={() => setStatusFilter(s)}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Severity chips */}
        <div className="filter-row" style={{ margin: 0 }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginRight: 4 }}>Severity:</span>
          {SEVERITY_FILTERS.map(s => (
            <button
              key={s}
              className={`filter-chip${severityFilter === s ? ` active chip-${s}` : ''}`}
              onClick={() => setSeverityFilter(s)}
            >
              {s}
            </button>
          ))}
        </div>

        <button className="btn btn-secondary btn-sm" onClick={refetch} disabled={loading}>
          {loading ? 'Loading…' : '↻'}
        </button>
      </div>

      {/* ── Disruption cards ──────────────────────────────────────────────────── */}
      {loading ? (
        <div className="table-wrapper"><SkeletonTable rows={5} cols={7} /></div>
      ) : error ? (
        <ErrorState message={error.message} onRetry={refetch} />
      ) : filtered.length === 0 ? (
        <EmptyState
          title={disruptions.length === 0 ? 'No disruptions found' : 'No results match your filters'}
          message="Try adjusting your search or filters."
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          {filtered.map(d => (
            <DisruptionCard
              key={d.disruption_id}
              disruption={d}
              onAnalyze={handleAnalyze}
              analyzing={analyzing && drawerDisruption?.disruption_id === d.disruption_id}
            />
          ))}
        </div>
      )}

      {/* ── Drawer ──────────────────────────────────────────────────────────── */}
      <Drawer
        isOpen={!!drawerDisruption}
        onClose={closeDrawer}
        title={drawerDisruption ? `${drawerDisruption.disruption_id} — ${drawerDisruption.location}` : ''}
      >
        {drawerDisruption && (
          <DisruptionDrawerContent
            disruption={drawerDisruption}
            analysisResult={analysisResult}
            analyzing={analyzing}
          />
        )}
      </Drawer>
    </div>
  )
}

// ── Disruption Card ───────────────────────────────────────────────────────────

function DisruptionCard({ disruption: d, onAnalyze, analyzing }) {
  return (
    <div className={`disruption-card severity-${d.severity}`}>
      <div className="disruption-card-header">
        <div>
          <div className="disruption-card-title">{d.location}</div>
          <div className="disruption-card-location">
            <span className="id-cell">{d.disruption_id}</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center', flexShrink: 0 }}>
          <RiskBadge level={d.severity} dot />
          <StatusBadge status={d.status} />
        </div>
      </div>
      <div className="disruption-card-meta" style={{ marginBottom: 'var(--space-3)' }}>
        <span className="disruption-card-meta-item"><TypeBadge type={d.type} /></span>
        <span className="disruption-card-meta-item">
          <span style={{ color: 'var(--text-muted)' }}>Duration:</span>&nbsp;
          <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{d.duration_days}d</span>
        </span>
      </div>
      <p className="disruption-card-desc">{d.description}</p>
      <div className="disruption-card-footer">
        <div className="disruption-card-stats" />
        <button
          className="btn btn-blue btn-sm"
          onClick={() => onAnalyze(d)}
          disabled={analyzing}
          aria-label={`Analyze impact of ${d.disruption_id}`}
        >
          <Zap size={12} />
          {analyzing ? 'Analyzing…' : 'Analyze Impact'}
        </button>
      </div>
    </div>
  )
}

// ── Drawer content ────────────────────────────────────────────────────────────

function DisruptionDrawerContent({ disruption: d, analysisResult, analyzing }) {
  return (
    <>
      {/* Overview */}
      <div>
        <div className="drawer-section-title">Disruption Overview</div>
        <div className="detail-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
          <div className="detail-field">
            <label>Type</label>
            <div className="field-value"><TypeBadge type={d.type} /></div>
          </div>
          <div className="detail-field">
            <label>Severity</label>
            <div className="field-value"><RiskBadge level={d.severity} dot /></div>
          </div>
          <div className="detail-field">
            <label>Location</label>
            <div className="field-value">{d.location}</div>
          </div>
          <div className="detail-field">
            <label>Duration</label>
            <div className="field-value" style={{ fontFamily: 'var(--font-mono)' }}>{d.duration_days} days</div>
          </div>
          <div className="detail-field" style={{ gridColumn: '1 / -1' }}>
            <label>Description</label>
            <div className="field-value" style={{ whiteSpace: 'normal', lineHeight: 1.6 }}>{d.description}</div>
          </div>
          <div className="detail-field">
            <label>Status</label>
            <div className="field-value"><StatusBadge status={d.status} /></div>
          </div>
          <div className="detail-field">
            <label>Disruption ID</label>
            <div className="field-value mono">{d.disruption_id}</div>
          </div>
        </div>
      </div>

      {/* Impact Analysis */}
      <div>
        <div className="drawer-section-title">Impact Analysis</div>
        {analyzing ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[1,2,3].map(i => <div key={i} className="skeleton skeleton-text" />)}
          </div>
        ) : !analysisResult ? (
          <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>
            Analysis not run yet. Results will appear here automatically.
          </p>
        ) : (
          <AnalysisResultSection result={analysisResult} />
        )}
      </div>
    </>
  )
}

// ── Analysis result section ───────────────────────────────────────────────────

function AnalysisResultSection({ result }) {
  const { summary, affected_shipments } = result

  return (
    <>
      {/* Summary row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
        {[
          { label: 'Affected', value: summary.total_affected },
          { label: 'Est. Impact', value: <CurrencyDisplay value={summary.estimated_impact} /> },
          { label: 'Avg Delay', value: summary.estimated_delay_days != null ? `${summary.estimated_delay_days}d` : '—' },
        ].map(({ label, value }) => (
          <div key={label} style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 'var(--space-3)' }}>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginBottom: 2 }}>{label}</div>
            <div style={{ fontWeight: 700, fontSize: 'var(--text-lg)', color: 'var(--text-bright)' }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Risk distribution */}
      <div style={{ marginBottom: 'var(--space-4)' }}>
        <RiskDistributionBar distribution={summary} />
      </div>

      {/* Affected shipments */}
      {affected_shipments?.length > 0 && (
        <>
          <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 'var(--space-2)' }}>
            Affected Shipments ({affected_shipments.length})
          </div>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Route</th>
                  <th>Cargo</th>
                  <th>Value</th>
                  <th>Risk</th>
                  <th>Score</th>
                  <th>Delay</th>
                </tr>
              </thead>
              <tbody>
                {affected_shipments
                  .slice()
                  .sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0))
                  .map(s => (
                    <tr key={s.shipment_id}>
                      <td><span className="id-cell">{s.shipment_id}</span></td>
                      <td style={{ fontSize: 'var(--text-xs)' }}>{s.origin?.split(',')[0]} → {s.destination?.split(',')[0]}</td>
                      <td>{s.cargo_type}</td>
                      <td><CurrencyDisplay value={s.cargo_value} /></td>
                      <td><RiskBadge level={s.risk_level} dot /></td>
                      <td><RiskScoreBar score={s.risk_score} level={s.risk_level} /></td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>{s.estimated_delay_days}d</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  )
}
