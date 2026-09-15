/**
 * RouteX — What-If Simulator: Professional decision-support tool.
 *
 * Consumes: GET /api/disruptions, POST /api/what-if (Member 4)
 */

import React, { useState } from 'react'
import { FlaskConical, Play, ArrowRight } from 'lucide-react'

import { useApi, useApiMutation } from '../hooks/useApi.js'
import { fetchDisruptions, runWhatIf } from '../services/api.js'
import {
  ErrorState, EmptyState, SectionCard, AlertBanner,
  RiskBadge, CurrencyDisplay,
} from '../components/common/index.jsx'
import { formatDisruptionType } from '../utils/format.js'
import { useAppContext } from '../context/AppContext.jsx'

const SEVERITY_OPTIONS = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
const DURATION_PRESETS = [1, 3, 5, 7, 14, 21]

export default function WhatIf() {
  const { addToast } = useAppContext()
  const [selectedDisruption, setSelectedDisruption] = useState('')
  const [durationDays, setDurationDays] = useState(7)
  const [severity, setSeverity] = useState('HIGH')
  const [scenarioResult, setScenarioResult] = useState(null)
  const [endpointUnavailable, setEndpointUnavailable] = useState(false)

  const { data: disruptionData, loading: disLoading } = useApi(() => fetchDisruptions())
  const disruptions = disruptionData?.data || []

  const { loading: simulating, execute: simulate } = useApiMutation(runWhatIf)

  const handleSimulate = async (e) => {
    e.preventDefault()
    if (!selectedDisruption) return
    setScenarioResult(null)
    setEndpointUnavailable(false)

    try {
      const result = await simulate({
        disruption_id: selectedDisruption,
        duration_days: Number(durationDays),
        severity,
      })
      setScenarioResult(result?.data || result)
      addToast('Simulation complete', 'success')
    } catch (err) {
      if (err.status === 404 || err.status === 405) {
        setEndpointUnavailable(true)
      } else {
        addToast(`Simulation failed: ${err.message}`, 'error')
      }
    }
  }

  const selectedD = disruptions.find(d => d.disruption_id === selectedDisruption)

  return (
    <div>
      <div className="section-row cols-2-1">
        {/* ── Configuration ──────────────────────────────────────────────────── */}
        <SectionCard title="Scenario Configuration">
          <form onSubmit={handleSimulate} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div className="form-group">
              <label htmlFor="wif-disruption">Disruption Event</label>
              {disLoading ? (
                <select disabled><option>Loading disruptions…</option></select>
              ) : (
                <select
                  id="wif-disruption"
                  value={selectedDisruption}
                  onChange={e => setSelectedDisruption(e.target.value)}
                  required
                >
                  <option value="">— Select a disruption —</option>
                  {disruptions.map(d => (
                    <option key={d.disruption_id} value={d.disruption_id}>
                      {d.disruption_id} · {d.location} ({formatDisruptionType(d.type)}) [{d.severity}]
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Selected disruption context */}
            {selectedD && (
              <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 'var(--space-3)', fontSize: 'var(--text-xs)' }}>
                <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Current severity: <RiskBadge level={selectedD.severity} /></span>
                  <span style={{ color: 'var(--text-muted)' }}>Duration: <strong style={{ color: 'var(--text-primary)' }}>{selectedD.duration_days}d</strong></span>
                </div>
              </div>
            )}

            <div>
              <label className="form-group" style={{ marginBottom: 'var(--space-2)', display: 'block', fontSize: 'var(--text-xs)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-secondary)' }}>
                Scenario Duration
              </label>
              <div className="duration-selector">
                {DURATION_PRESETS.map(d => (
                  <button
                    type="button"
                    key={d}
                    className={`duration-btn${durationDays === d ? ' active' : ''}`}
                    onClick={() => setDurationDays(d)}
                  >
                    {d}d
                  </button>
                ))}
              </div>
              <input
                type="number" min={1} max={365}
                value={durationDays}
                onChange={e => setDurationDays(Number(e.target.value))}
                style={{ width: 80, marginTop: 'var(--space-2)' }}
                aria-label="Custom duration in days"
              />
            </div>

            <div className="form-group">
              <label htmlFor="wif-severity">Scenario Severity</label>
              <select
                id="wif-severity"
                value={severity}
                onChange={e => setSeverity(e.target.value)}
              >
                {SEVERITY_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={simulating || !selectedDisruption}
            >
              <Play size={14} />
              {simulating ? 'Simulating…' : 'Run Simulation'}
            </button>
          </form>
        </SectionCard>

        {/* ── Results ────────────────────────────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {endpointUnavailable ? (
            <SectionCard>
              <AlertBanner type="warning">
                <div>
                  <strong>What-If endpoint not yet available.</strong><br />
                  <span style={{ fontSize: 'var(--text-xs)' }}>POST /api/what-if is provided by Member 4. This interface is ready to consume it.</span>
                </div>
              </AlertBanner>
            </SectionCard>
          ) : simulating ? (
            <SectionCard>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: 'var(--space-4)' }}>
                {[1,2,3,4].map(i => <div key={i} className="skeleton skeleton-text" />)}
              </div>
            </SectionCard>
          ) : scenarioResult ? (
            <WhatIfResultView result={scenarioResult} />
          ) : (
            <SectionCard>
              <EmptyState
                title="Configure a scenario"
                message="Select a disruption, set duration and severity, then click Run Simulation."
              />
            </SectionCard>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Result view ───────────────────────────────────────────────────────────────

function WhatIfResultView({ result }) {
  const { baseline, scenario, difference, affected_shipments, recommended_actions } = result

  return (
    <>
      {/* Comparison */}
      {(baseline || scenario) && (
        <SectionCard title="Scenario Comparison">
          <div className="comparison-grid">
            <div className="comparison-panel">
              <div className="comparison-panel-header baseline">Baseline</div>
              {baseline && Object.entries(baseline).map(([key, val]) => (
                <div key={key} className="comparison-metric">
                  <span className="comparison-metric-label" style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}</span>
                  <span className="comparison-metric-val">{val ?? '—'}</span>
                </div>
              ))}
            </div>
            <div className="comparison-arrow"><ArrowRight size={20} /></div>
            <div className="comparison-panel">
              <div className="comparison-panel-header scenario">Scenario</div>
              {scenario && Object.entries(scenario).map(([key, val]) => {
                const diff = difference?.[key]
                return (
                  <div key={key} className="comparison-metric">
                    <span className="comparison-metric-label" style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}</span>
                    <span className="comparison-metric-val">
                      {val ?? '—'}
                      {diff != null && (
                        <span className={diff > 0 ? 'diff-negative' : 'diff-positive'} style={{ marginLeft: 6, fontSize: 'var(--text-xs)' }}>
                          {diff > 0 ? `+${diff}` : diff}
                        </span>
                      )}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </SectionCard>
      )}

      {/* Affected shipments */}
      {affected_shipments?.length > 0 && (
        <SectionCard title={`Affected Shipments (${affected_shipments.length})`}>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr><th>Shipment</th><th>Risk</th><th>Est. Impact</th></tr>
              </thead>
              <tbody>
                {affected_shipments.map((s, i) => (
                  <tr key={s.shipment_id || i}>
                    <td><span className="id-cell">{s.shipment_id || '—'}</span></td>
                    <td><RiskBadge level={s.risk_level} dot /></td>
                    <td><CurrencyDisplay value={s.estimated_impact} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      )}

      {/* Recommended actions */}
      {recommended_actions?.length > 0 && (
        <SectionCard title="Recommended Actions">
          <ol style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {recommended_actions.map((action, i) => (
              <li
                key={i}
                style={{ display: 'flex', gap: 'var(--space-3)', padding: 'var(--space-3)', background: 'var(--bg-elevated)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}
              >
                <span style={{ width: 22, height: 22, borderRadius: 'var(--radius-sm)', background: 'var(--blue-dim)', border: '1px solid rgba(56,139,253,0.3)', color: 'var(--blue-bright)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 'var(--text-xs)', fontWeight: 700, flexShrink: 0 }}>
                  {i + 1}
                </span>
                <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                  {typeof action === 'string' ? action : action.action || JSON.stringify(action)}
                </span>
              </li>
            ))}
          </ol>
        </SectionCard>
      )}

      {/* Fallback — raw result */}
      {!baseline && !scenario && !affected_shipments && (
        <SectionCard title="Simulation Result">
          <pre style={{ background: 'var(--bg-elevated)', padding: 'var(--space-4)', borderRadius: 'var(--radius)', fontSize: 'var(--text-xs)', fontFamily: 'var(--font-mono)', overflow: 'auto', color: 'var(--text-secondary)' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </SectionCard>
      )}
    </>
  )
}
