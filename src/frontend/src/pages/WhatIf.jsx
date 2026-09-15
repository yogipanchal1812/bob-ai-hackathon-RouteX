/**
 * RouteX Frontend — What-If Simulator page.
 *
 * Consumes: GET /api/disruptions, POST /api/what-if (Member 4 — may not yet be available)
 * Allows user to configure a scenario and compare baseline vs result.
 */

import React, { useState } from 'react'

import { useApi, useApiMutation } from '../hooks/useApi.js'
import { fetchDisruptions, runWhatIf } from '../services/api.js'
import {
  LoadingState, ErrorState, EmptyState, SectionCard, AlertBanner,
  RiskBadge, CurrencyDisplay, PageHeader,
} from '../components/common/index.jsx'
import { formatDisruptionType } from '../utils/format.js'

const SEVERITY_OPTIONS = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

export default function WhatIf() {
  const [selectedDisruption, setSelectedDisruption] = useState('')
  const [durationDays, setDurationDays] = useState(7)
  const [severity, setSeverity] = useState('HIGH')
  const [scenarioResult, setScenarioResult] = useState(null)
  const [scenarioError, setScenarioError] = useState(null)
  const [endpointUnavailable, setEndpointUnavailable] = useState(false)

  // ── Fetch disruption options ───────────────────────────────────────────────
  const { data: disruptionData, loading: disLoading } = useApi(() => fetchDisruptions())
  const disruptions = disruptionData?.data || []

  // ── What-if mutation ──────────────────────────────────────────────────────
  const { loading: simulating, execute: simulate } = useApiMutation(runWhatIf)

  const handleSimulate = async (e) => {
    e.preventDefault()
    if (!selectedDisruption) return
    setScenarioResult(null)
    setScenarioError(null)
    setEndpointUnavailable(false)

    try {
      const result = await simulate({
        disruption_id: selectedDisruption,
        duration_days: Number(durationDays),
        severity,
      })
      setScenarioResult(result?.data || result)
    } catch (err) {
      if (err.status === 404 || err.status === 405) {
        setEndpointUnavailable(true)
      } else {
        setScenarioError(err.message || 'Simulation failed.')
      }
    }
  }

  return (
    <div>
      <PageHeader
        title="What-If Simulator"
        subtitle="Simulate disruption scenarios and compare baseline vs projected impact"
      />

      <div className="section-row cols-2">
        {/* ── Configuration panel ──────────────────────────────────────────── */}
        <SectionCard title="Scenario Configuration">
          <form onSubmit={handleSimulate} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div className="form-group">
              <label htmlFor="wif-disruption">Disruption</label>
              {disLoading ? (
                <select disabled><option>Loading…</option></select>
              ) : (
                <select
                  id="wif-disruption"
                  value={selectedDisruption}
                  onChange={e => setSelectedDisruption(e.target.value)}
                  required
                  aria-required="true"
                >
                  <option value="">— Select a disruption —</option>
                  {disruptions.map(d => (
                    <option key={d.disruption_id} value={d.disruption_id}>
                      {d.disruption_id} — {d.location} ({d.type.replace(/_/g, ' ')})
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="wif-duration">Scenario Duration (days)</label>
              <input
                id="wif-duration"
                type="number"
                min={1}
                max={365}
                value={durationDays}
                onChange={e => setDurationDays(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="wif-severity">Severity</label>
              <select
                id="wif-severity"
                value={severity}
                onChange={e => setSeverity(e.target.value)}
              >
                {SEVERITY_OPTIONS.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={simulating || !selectedDisruption}
            >
              {simulating ? 'Simulating…' : '▶ Run Simulation'}
            </button>
          </form>
        </SectionCard>

        {/* ── Results panel ────────────────────────────────────────────────── */}
        <SectionCard title="Simulation Results">
          {endpointUnavailable ? (
            <AlertBanner type="warning">
              <div>
                <strong>What-If endpoint not yet available.</strong>
                <br />
                <span style={{ fontSize: 'var(--text-sm)' }}>
                  POST /api/what-if is provided by Member 4.
                  This interface is ready and will display results once the endpoint is live.
                </span>
              </div>
            </AlertBanner>
          ) : scenarioError ? (
            <AlertBanner type="error">{scenarioError}</AlertBanner>
          ) : simulating ? (
            <LoadingState message="Running scenario simulation…" />
          ) : scenarioResult ? (
            <WhatIfResultView result={scenarioResult} />
          ) : (
            <EmptyState
              title="No simulation run yet"
              message="Configure a scenario on the left and click Run Simulation."
              icon="🔬"
            />
          )}
        </SectionCard>
      </div>
    </div>
  )
}

// ── Result sub-component ──────────────────────────────────────────────────────

function WhatIfResultView({ result }) {
  const { baseline, scenario, difference, affected_shipments, recommended_actions } = result

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      {/* Comparison table */}
      {(baseline || scenario || difference) && (
        <div>
          <div className="section-title" style={{ marginBottom: 'var(--space-3)' }}>Scenario Comparison</div>
          <div className="table-wrapper">
            <table className="data-table diff-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Baseline</th>
                  <th>Scenario</th>
                  <th>Difference</th>
                </tr>
              </thead>
              <tbody>
                {baseline && Object.entries(baseline).map(([key, val]) => {
                  const scenVal = scenario?.[key]
                  const diffVal = difference?.[key]
                  const isNeg = typeof diffVal === 'number' && diffVal > 0
                  const isPos = typeof diffVal === 'number' && diffVal < 0
                  return (
                    <tr key={key}>
                      <td style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}</td>
                      <td>{val ?? '—'}</td>
                      <td>{scenVal ?? '—'}</td>
                      <td className={isNeg ? 'diff-neg' : isPos ? 'diff-pos' : ''}>
                        {diffVal != null ? (diffVal > 0 ? `+${diffVal}` : diffVal) : '—'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Affected shipments */}
      {affected_shipments?.length > 0 && (
        <div>
          <div className="section-title" style={{ marginBottom: 'var(--space-3)' }}>
            Affected Shipments ({affected_shipments.length})
          </div>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Shipment ID</th>
                  <th>Risk</th>
                  <th>Impact</th>
                </tr>
              </thead>
              <tbody>
                {affected_shipments.map((s, i) => (
                  <tr key={s.shipment_id || i}>
                    <td><span className="id-cell">{s.shipment_id || '—'}</span></td>
                    <td><RiskBadge level={s.risk_level} /></td>
                    <td><CurrencyDisplay value={s.estimated_impact} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recommended actions */}
      {recommended_actions?.length > 0 && (
        <div>
          <div className="section-title" style={{ marginBottom: 'var(--space-3)' }}>Recommended Actions</div>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            {recommended_actions.map((action, i) => (
              <li
                key={i}
                style={{
                  padding: 'var(--space-3)',
                  background: 'var(--bg-surface)',
                  borderRadius: 'var(--radius)',
                  fontSize: 'var(--text-sm)',
                  display: 'flex',
                  gap: 'var(--space-2)',
                  alignItems: 'flex-start',
                }}
              >
                <span style={{ color: 'var(--accent-blue)', marginTop: 2 }}>→</span>
                <span>{typeof action === 'string' ? action : JSON.stringify(action)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Fallback — display raw result if structure unknown */}
      {!baseline && !scenario && !affected_shipments && (
        <div>
          <div className="section-title" style={{ marginBottom: 'var(--space-3)' }}>Result</div>
          <pre
            style={{
              background: 'var(--bg-surface)',
              padding: 'var(--space-4)',
              borderRadius: 'var(--radius)',
              fontSize: 'var(--text-xs)',
              fontFamily: 'var(--font-mono)',
              overflow: 'auto',
              color: 'var(--text-secondary)',
            }}
          >
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
