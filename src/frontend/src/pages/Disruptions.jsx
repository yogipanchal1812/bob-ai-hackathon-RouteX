/**
 * RouteX Frontend — Disruptions page.
 *
 * Consumes: GET /api/disruptions, POST /api/analyze-disruption
 * Displays: Disruption list + per-disruption analysis with affected shipments.
 */

import React, { useState } from 'react'

import { useApi, useApiMutation } from '../hooks/useApi.js'
import { fetchDisruptions, analyzeDisruption } from '../services/api.js'
import {
  LoadingState, ErrorState, EmptyState, SectionCard, AlertBanner,
  RiskBadge, StatusBadge, CurrencyDisplay, RiskScoreBar, PageHeader, RiskDistributionBar,
} from '../components/common/index.jsx'
import { formatDisruptionType } from '../utils/format.js'

const STATUS_OPTIONS = ['', 'ACTIVE', 'MONITORING', 'RESOLVED']

export default function Disruptions() {
  const [statusFilter, setStatusFilter] = useState('ACTIVE')
  const [selectedDisruption, setSelectedDisruption] = useState(null)
  const [analysisAlert, setAnalysisAlert] = useState(null)

  // ── Fetch disruptions ──────────────────────────────────────────────────────
  const { data, loading, error, refetch } = useApi(
    () => fetchDisruptions(statusFilter ? { status: statusFilter } : {}),
    [statusFilter]
  )
  const disruptions = data?.data || []

  // ── Analyze mutation ───────────────────────────────────────────────────────
  const {
    data: analysisData,
    loading: analyzing,
    error: analysisError,
    execute: runAnalysis,
  } = useApiMutation(analyzeDisruption)

  const analysisResult = analysisData?.data

  const handleAnalyze = async (disruption) => {
    setSelectedDisruption(disruption)
    setAnalysisAlert(null)
    try {
      await runAnalysis(disruption.disruption_id)
    } catch (err) {
      setAnalysisAlert(err.message || 'Analysis failed.')
    }
  }

  return (
    <div>
      <PageHeader
        title="Disruptions"
        subtitle="Active supply-chain disruption events and impact analysis"
        actions={
          <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <select
                value={statusFilter}
                onChange={e => { setStatusFilter(e.target.value); setSelectedDisruption(null) }}
                style={{ minWidth: 140 }}
                aria-label="Filter by status"
              >
                <option value="">All Statuses</option>
                {STATUS_OPTIONS.filter(Boolean).map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={refetch} disabled={loading}>
              {loading ? 'Loading…' : '↻ Refresh'}
            </button>
          </div>
        }
      />

      {/* ── Disruption list ──────────────────────────────────────────────────── */}
      <div className="mb-6">
        <SectionCard title={`Disruptions ${disruptions.length > 0 ? `(${disruptions.length})` : ''}`}>
          {loading ? (
            <LoadingState message="Loading disruptions…" />
          ) : error ? (
            <ErrorState message={error.message} onRetry={refetch} />
          ) : disruptions.length === 0 ? (
            <EmptyState
              title="No disruptions found"
              message={statusFilter ? `No disruptions with status "${statusFilter}".` : 'No disruption events in the system.'}
              icon="✅"
            />
          ) : (
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Location</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Duration</th>
                    <th>Status</th>
                    <th>Description</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {disruptions.map(d => (
                    <tr
                      key={d.disruption_id}
                      className={selectedDisruption?.disruption_id === d.disruption_id ? 'selected' : ''}
                    >
                      <td><span className="id-cell">{d.disruption_id}</span></td>
                      <td>{d.location}</td>
                      <td>{formatDisruptionType(d.type)}</td>
                      <td><RiskBadge level={d.severity} /></td>
                      <td>{d.duration_days}d</td>
                      <td><StatusBadge status={d.status} /></td>
                      <td className="wrap" style={{ maxWidth: 260, whiteSpace: 'normal' }}>{d.description}</td>
                      <td>
                        <button
                          className="btn btn-blue btn-sm"
                          onClick={() => handleAnalyze(d)}
                          disabled={analyzing && selectedDisruption?.disruption_id === d.disruption_id}
                          aria-label={`Analyze disruption ${d.disruption_id}`}
                        >
                          {analyzing && selectedDisruption?.disruption_id === d.disruption_id
                            ? 'Analyzing…'
                            : 'Analyze'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>
      </div>

      {/* ── Analysis result ──────────────────────────────────────────────────── */}
      {(selectedDisruption || analyzing || analysisResult) && (
        <div className="mb-6">
          <SectionCard
            title={
              selectedDisruption
                ? `Impact Analysis — ${selectedDisruption.disruption_id} · ${selectedDisruption.location}`
                : 'Impact Analysis'
            }
          >
            {analysisAlert && (
              <AlertBanner type="error" onClose={() => setAnalysisAlert(null)}>
                {analysisAlert}
              </AlertBanner>
            )}

            {analyzing ? (
              <LoadingState message="Running impact analysis…" />
            ) : analysisError && !analysisAlert ? (
              <ErrorState
                message={analysisError.message}
                onRetry={() => selectedDisruption && handleAnalyze(selectedDisruption)}
              />
            ) : analysisResult ? (
              <AnalysisResultView result={analysisResult} />
            ) : (
              <EmptyState
                title="Select a disruption to analyze"
                message="Click the Analyze button on any disruption above."
                icon="🔍"
              />
            )}
          </SectionCard>
        </div>
      )}
    </div>
  )
}

// ── Analysis result sub-component ────────────────────────────────────────────

function AnalysisResultView({ result }) {
  const { disruption_id, disruption_type, disruption_severity, disruption_location, affected_shipments, summary } = result

  return (
    <div>
      {/* Header meta */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-5)',
          paddingBottom: 'var(--space-4)',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <div>
          <div className="kpi-label">Type</div>
          <div style={{ fontWeight: 600 }}>{formatDisruptionType(disruption_type)}</div>
        </div>
        <div>
          <div className="kpi-label">Severity</div>
          <div><RiskBadge level={disruption_severity} /></div>
        </div>
        <div>
          <div className="kpi-label">Location</div>
          <div style={{ fontWeight: 600 }}>{disruption_location}</div>
        </div>
        <div>
          <div className="kpi-label">Affected</div>
          <div style={{ fontWeight: 700, fontSize: 'var(--text-xl)' }}>{summary.total_affected}</div>
        </div>
        <div>
          <div className="kpi-label">Est. Impact</div>
          <div style={{ fontWeight: 700, fontSize: 'var(--text-xl)' }}>
            <CurrencyDisplay value={summary.estimated_impact} />
          </div>
        </div>
        <div>
          <div className="kpi-label">Avg Delay</div>
          <div style={{ fontWeight: 600 }}>{summary.estimated_delay_days}d</div>
        </div>
      </div>

      {/* Risk distribution */}
      <div style={{ marginBottom: 'var(--space-5)' }}>
        <div className="section-title" style={{ marginBottom: 'var(--space-3)' }}>Risk Distribution</div>
        <RiskDistributionBar distribution={summary} />
      </div>

      {/* Affected shipments */}
      {affected_shipments.length === 0 ? (
        <EmptyState title="No affected shipments" message="No shipments are exposed to this disruption." icon="✅" />
      ) : (
        <>
          <div className="section-title">Affected Shipments ({affected_shipments.length})</div>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Shipment ID</th>
                  <th>Origin → Destination</th>
                  <th>Cargo</th>
                  <th>Value</th>
                  <th>Priority</th>
                  <th>Risk Score</th>
                  <th>Risk Level</th>
                  <th>Delay</th>
                  <th>Est. Impact</th>
                </tr>
              </thead>
              <tbody>
                {affected_shipments
                  .slice()
                  .sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0))
                  .map(s => (
                    <tr key={s.shipment_id}>
                      <td><span className="id-cell">{s.shipment_id}</span></td>
                      <td>{s.origin} → {s.destination}</td>
                      <td>{s.cargo_type}</td>
                      <td><CurrencyDisplay value={s.cargo_value} /></td>
                      <td><RiskBadge level={s.priority} /></td>
                      <td>
                        <RiskScoreBar score={s.risk_score} level={s.risk_level} />
                      </td>
                      <td><RiskBadge level={s.risk_level} /></td>
                      <td>{s.estimated_delay_days}d</td>
                      <td><CurrencyDisplay value={s.estimated_impact} /></td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
