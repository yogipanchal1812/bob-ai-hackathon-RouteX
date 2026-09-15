/**
 * RouteX Frontend — Dashboard page.
 *
 * Consumes: GET /api/impact-summary, GET /api/disruptions, GET /api/shipments
 * Displays: KPI cards, risk distribution, active disruptions, affected shipments, chart.
 */

import React, { useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'

import { useApi } from '../hooks/useApi.js'
import { fetchImpactSummary, fetchDisruptions, fetchShipments } from '../services/api.js'
import {
  LoadingState, ErrorState, EmptyState, SectionCard,
  RiskBadge, StatusBadge, CurrencyDisplay, RiskDistributionBar, PageHeader,
} from '../components/common/index.jsx'
import { formatDate, formatDisruptionType, formatCurrency } from '../utils/format.js'

// ── Risk chart colors ─────────────────────────────────────────────────────────
const RISK_COLORS = {
  LOW: '#3fb950',
  MEDIUM: '#d29922',
  HIGH: '#f85149',
  CRITICAL: '#da3633',
}

// ── KPI Card ──────────────────────────────────────────────────────────────────
function KpiCard({ label, value, sub, variant }) {
  return (
    <div className={`kpi-card${variant ? ` kpi-${variant}` : ''}`}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value ?? '—'}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  )
}

// ── Disruption bar chart data ─────────────────────────────────────────────────
function buildDisruptionBarData(disruptions) {
  return (disruptions || []).map(d => ({
    name: d.location,
    affected: d.total_affected || 0,
    impact: d.estimated_impact || 0,
  }))
}

// ── Risk pie data ─────────────────────────────────────────────────────────────
function buildRiskPieData(dist) {
  if (!dist) return []
  const entries = [
    { name: 'LOW', value: dist.low_risk || 0 },
    { name: 'MEDIUM', value: dist.medium_risk || 0 },
    { name: 'HIGH', value: dist.high_risk || 0 },
    { name: 'CRITICAL', value: dist.critical_risk || 0 },
  ]
  return entries.filter(e => e.value > 0)
}

// ── Affected shipment row ─────────────────────────────────────────────────────
function AffectedShipmentRow({ shipment }) {
  return (
    <tr>
      <td><span className="id-cell">{shipment.shipment_id}</span></td>
      <td>{shipment.origin}</td>
      <td>{shipment.destination}</td>
      <td><RiskBadge level={shipment.risk_level} /></td>
      <td>{shipment.risk_score ?? '—'}</td>
      <td><CurrencyDisplay value={shipment.cargo_value} /></td>
      <td>{shipment.priority}</td>
      <td>{shipment.estimated_delay_days != null ? `${shipment.estimated_delay_days}d` : '—'}</td>
    </tr>
  )
}

export default function Dashboard() {
  // ── Data fetching ────────────────────────────────────────────────────────────
  const summary = useApi(() => fetchImpactSummary())
  const disruptions = useApi(() => fetchDisruptions({ status: 'ACTIVE' }))
  const shipments = useApi(() => fetchShipments())

  const impactData = summary.data?.data
  const activeDisruptions = disruptions.data?.data || []
  const allShipments = shipments.data?.data || []

  // ── Derived KPIs ─────────────────────────────────────────────────────────────
  const highRiskShipments = useMemo(
    () => allShipments.filter(s => s.risk_level === 'HIGH' || s.risk_level === 'CRITICAL'),
    [allShipments]
  )
  const criticalShipments = useMemo(
    () => allShipments.filter(s => s.risk_level === 'CRITICAL'),
    [allShipments]
  )

  // Collect all affected shipments from disruption analysis for the table
  const affectedShipments = useMemo(() => {
    if (!impactData?.disruptions) return []
    // We show the disruption-level summary; detailed per-shipment table is in Disruptions page
    return impactData.disruptions
  }, [impactData])

  const barData = useMemo(() => buildDisruptionBarData(impactData?.disruptions), [impactData])
  const pieData = useMemo(() => buildRiskPieData(impactData?.risk_distribution), [impactData])

  const isLoading = summary.loading || disruptions.loading || shipments.loading
  const hasError = summary.error && disruptions.error

  return (
    <div>
      <PageHeader
        title="Supply Chain Command Center"
        subtitle="Real-time disruption intelligence and risk overview"
        actions={
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => { summary.refetch(); disruptions.refetch(); shipments.refetch() }}
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing…' : '↻ Refresh'}
          </button>
        }
      />

      {/* ── KPI Cards ────────────────────────────────────────────────────────── */}
      {summary.loading ? (
        <div className="kpi-grid">
          {Array(5).fill(0).map((_, i) => (
            <div key={i} className="kpi-card" style={{ opacity: 0.5 }}>
              <div className="kpi-label">Loading…</div>
              <div className="kpi-value">—</div>
            </div>
          ))}
        </div>
      ) : summary.error ? (
        <div className="kpi-grid">
          <div className="kpi-card" style={{ gridColumn: '1 / -1' }}>
            <ErrorState
              message={summary.error.message}
              onRetry={summary.refetch}
            />
          </div>
        </div>
      ) : (
        <div className="kpi-grid">
          <KpiCard
            label="Active Disruptions"
            value={impactData?.total_active_disruptions ?? '—'}
            sub="Affecting active routes"
            variant="critical"
          />
          <KpiCard
            label="Affected Shipments"
            value={impactData?.total_affected_shipments ?? '—'}
            sub="Across all disruptions"
            variant="high"
          />
          <KpiCard
            label="High-Risk Shipments"
            value={shipments.loading ? '…' : highRiskShipments.length}
            sub="HIGH or CRITICAL level"
            variant="high"
          />
          <KpiCard
            label="Critical Shipments"
            value={shipments.loading ? '…' : criticalShipments.length}
            sub="CRITICAL risk level"
            variant="critical"
          />
          <KpiCard
            label="Estimated Impact"
            value={impactData ? formatCurrency(impactData.total_estimated_impact) : '—'}
            sub="Total financial exposure"
            variant="warning"
          />
        </div>
      )}

      {/* ── Charts row ───────────────────────────────────────────────────────── */}
      <div className="section-row cols-2 mb-6">
        <SectionCard title="Affected Shipments by Disruption">
          {summary.loading ? (
            <LoadingState />
          ) : summary.error ? (
            <ErrorState message={summary.error.message} onRetry={summary.refetch} />
          ) : barData.length === 0 ? (
            <EmptyState title="No active disruptions" message="No impact data to display." icon="✅" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} margin={{ top: 4, right: 8, bottom: 32, left: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: 'var(--text-secondary)' }}
                  angle={-30}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6 }}
                  labelStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
                  itemStyle={{ color: 'var(--text-secondary)' }}
                />
                <Bar dataKey="affected" name="Affected Shipments" fill="var(--accent-blue)" radius={[3,3,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        <SectionCard title="Risk Distribution">
          {summary.loading ? (
            <LoadingState />
          ) : summary.error ? (
            <ErrorState message={summary.error.message} onRetry={summary.refetch} />
          ) : pieData.length === 0 ? (
            <EmptyState title="No risk data" message="No affected shipments found." icon="✅" />
          ) : (
            <>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry) => (
                      <Cell key={entry.name} fill={RISK_COLORS[entry.name] || '#888'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6 }}
                    itemStyle={{ color: 'var(--text-secondary)' }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: 11, color: 'var(--text-secondary)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              {impactData?.risk_distribution && (
                <div style={{ marginTop: 'var(--space-3)' }}>
                  <RiskDistributionBar distribution={impactData.risk_distribution} />
                </div>
              )}
            </>
          )}
        </SectionCard>
      </div>

      {/* ── Active Disruptions ───────────────────────────────────────────────── */}
      <div className="mb-6">
        <SectionCard title="Active Disruptions">
          {disruptions.loading ? (
            <LoadingState />
          ) : disruptions.error ? (
            <ErrorState message={disruptions.error.message} onRetry={disruptions.refetch} />
          ) : activeDisruptions.length === 0 ? (
            <EmptyState title="No active disruptions" message="All corridors are clear." icon="✅" />
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
                  </tr>
                </thead>
                <tbody>
                  {activeDisruptions.map(d => (
                    <tr key={d.disruption_id}>
                      <td><span className="id-cell">{d.disruption_id}</span></td>
                      <td>{d.location}</td>
                      <td>{formatDisruptionType(d.type)}</td>
                      <td><RiskBadge level={d.severity} /></td>
                      <td>{d.duration_days}d</td>
                      <td><StatusBadge status={d.status} /></td>
                      <td className="wrap" style={{ maxWidth: 280, whiteSpace: 'normal' }}>{d.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>
      </div>

      {/* ── Impact by Disruption table ───────────────────────────────────────── */}
      <div className="mb-6">
        <SectionCard title="Disruption Impact Summary">
          {summary.loading ? (
            <LoadingState />
          ) : summary.error ? (
            <ErrorState message={summary.error.message} onRetry={summary.refetch} />
          ) : affectedShipments.length === 0 ? (
            <EmptyState title="No impact data" message="No disruptions are currently affecting shipments." icon="✅" />
          ) : (
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Disruption</th>
                    <th>Location</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Affected</th>
                    <th>Avg Delay</th>
                    <th>Est. Impact</th>
                  </tr>
                </thead>
                <tbody>
                  {affectedShipments.map(d => (
                    <tr key={d.disruption_id}>
                      <td><span className="id-cell">{d.disruption_id}</span></td>
                      <td>{d.location}</td>
                      <td>{formatDisruptionType(d.type)}</td>
                      <td><RiskBadge level={d.severity} /></td>
                      <td>{d.total_affected}</td>
                      <td>{d.estimated_delay_days != null ? `${d.estimated_delay_days}d` : '—'}</td>
                      <td><CurrencyDisplay value={d.estimated_impact} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>
      </div>
    </div>
  )
}
