/**
 * RouteX — Dashboard: Supply Chain Command Center
 *
 * Consumes: GET /api/impact-summary, GET /api/disruptions, GET /api/shipments
 */

import React, { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, RadialBarChart, RadialBar,
} from 'recharts'
import {
  Zap, Package, AlertOctagon, TrendingUp, DollarSign,
  ArrowRight, Bot, Ship,
} from 'lucide-react'

import { useApi } from '../hooks/useApi.js'
import { fetchImpactSummary, fetchDisruptions, fetchShipments } from '../services/api.js'
import {
  SkeletonKpiCard, SkeletonChart, SkeletonTable,
  ErrorState, EmptyState, SectionCard,
  RiskBadge, StatusBadge, CurrencyDisplay, RiskDistributionBar, TypeBadge,
} from '../components/common/index.jsx'
import { formatDate, formatDisruptionType, formatCurrency } from '../utils/format.js'

// ── Colors ────────────────────────────────────────────────────────────────────
const RISK_COLORS = {
  LOW: '#3fb950', MEDIUM: '#e3b341', HIGH: '#f0883e', CRITICAL: '#f85149',
}
const CHART_TOOLTIP_STYLE = {
  contentStyle: { background: '#111820', border: '1px solid #1e2d3d', borderRadius: 6, fontSize: 12 },
  labelStyle: { color: '#f0f6fc', fontWeight: 600 },
  itemStyle: { color: '#768390' },
}

// ── Compute supply chain health score from real data ─────────────────────────
function computeHealthScore(impactData, shipments) {
  if (!impactData || !shipments) return null
  const total = shipments.length || 1
  const dist = impactData.risk_distribution || {}
  const criticalW  = (dist.critical_risk || 0) * 4
  const highW      = (dist.high_risk || 0) * 2
  const mediumW    = (dist.medium_risk || 0) * 1
  const affected   = impactData.total_affected_shipments || 0
  const riskPenalty = Math.min(50, ((criticalW + highW + mediumW) / (total * 4)) * 50)
  const affectedPenalty = Math.min(30, (affected / total) * 30)
  const disruptions = impactData.total_active_disruptions || 0
  const disruptionPenalty = Math.min(20, disruptions * 4)
  return Math.max(0, Math.round(100 - riskPenalty - affectedPenalty - disruptionPenalty))
}

function healthColor(score) {
  if (score >= 70) return 'var(--risk-low)'
  if (score >= 40) return 'var(--risk-medium)'
  return 'var(--risk-high)'
}

// ── KPI Card ──────────────────────────────────────────────────────────────────
function KpiCard({ label, value, sub, variant, Icon, loading }) {
  if (loading) return <SkeletonKpiCard />
  return (
    <div className={`kpi-card${variant ? ` kpi-${variant}` : ''}`}>
      <div className="kpi-icon-row">
        <div className="kpi-label">{label}</div>
        {Icon && (
          <div className="kpi-icon">
            <Icon size={14} strokeWidth={2} />
          </div>
        )}
      </div>
      <div className="kpi-value">{value ?? '—'}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  )
}

// ── Health Gauge (SVG ring) ───────────────────────────────────────────────────
function HealthGauge({ score }) {
  const r = 42
  const circumference = 2 * Math.PI * r
  const progress = score != null ? (score / 100) * circumference : 0
  const color = healthColor(score ?? 50)
  return (
    <svg width={110} height={110} viewBox="0 0 110 110" role="img" aria-label={`Health score ${score}`}>
      <circle cx={55} cy={55} r={r} fill="none" stroke="var(--border)" strokeWidth={7} />
      <circle
        cx={55} cy={55} r={r} fill="none"
        stroke={color} strokeWidth={7}
        strokeDasharray={`${progress} ${circumference}`}
        strokeLinecap="round"
        transform="rotate(-90 55 55)"
        style={{ transition: 'stroke-dasharray 0.8s ease' }}
      />
      <text x={55} y={52} textAnchor="middle" fill={color} fontSize={22} fontWeight={800} fontFamily="system-ui">
        {score ?? '—'}
      </text>
      <text x={55} y={66} textAnchor="middle" fill="var(--text-muted)" fontSize={9} fontFamily="system-ui" fontWeight={500}>
        HEALTH
      </text>
    </svg>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()

  const summary    = useApi(() => fetchImpactSummary())
  const disruptions = useApi(() => fetchDisruptions({ status: 'ACTIVE' }))
  const shipments  = useApi(() => fetchShipments())

  const impactData        = summary.data?.data
  const activeDisruptions = disruptions.data?.data || []
  const allShipments      = shipments.data?.data || []

  const highRiskCount     = useMemo(() => allShipments.filter(s => s.risk_level === 'HIGH' || s.risk_level === 'CRITICAL').length, [allShipments])
  const criticalCount     = useMemo(() => allShipments.filter(s => s.risk_level === 'CRITICAL').length, [allShipments])
  const healthScore       = useMemo(() => computeHealthScore(impactData, allShipments), [impactData, allShipments])

  const barData = useMemo(() =>
    (impactData?.disruptions || []).map(d => ({
      name: d.location.split(',')[0],
      affected: d.total_affected || 0,
    })), [impactData])

  const pieData = useMemo(() => {
    const dist = impactData?.risk_distribution
    if (!dist) return []
    return [
      { name: 'LOW', value: dist.low_risk || 0 },
      { name: 'MEDIUM', value: dist.medium_risk || 0 },
      { name: 'HIGH', value: dist.high_risk || 0 },
      { name: 'CRITICAL', value: dist.critical_risk || 0 },
    ].filter(e => e.value > 0)
  }, [impactData])

  // Build AI insight text deterministically from real data
  const aiInsight = useMemo(() => {
    if (!impactData || !allShipments.length) return null
    const dist = impactData.risk_distribution || {}
    const critCount = dist.critical_risk || 0
    const highCount = dist.high_risk || 0
    const topDisruption = (impactData.disruptions || [])[0]
    if (critCount > 0) {
      return {
        headline: `${critCount} shipment${critCount !== 1 ? 's' : ''} classified as CRITICAL risk.`,
        detail: `${highCount} additional shipment${highCount !== 1 ? 's' : ''} at HIGH risk. ${topDisruption ? `The most severe active disruption is at ${topDisruption.location} (${topDisruption.severity}).` : ''}`,
        delay: impactData.disruptions?.[0]?.estimated_delay_days ?? null,
        impact: impactData.total_estimated_impact,
      }
    }
    if (highCount > 0) {
      return {
        headline: `${highCount} shipment${highCount !== 1 ? 's' : ''} at HIGH risk from active disruptions.`,
        detail: topDisruption ? `The disruption at ${topDisruption.location} is the primary contributing event.` : '',
        delay: impactData.disruptions?.[0]?.estimated_delay_days ?? null,
        impact: impactData.total_estimated_impact,
      }
    }
    return {
      headline: `${impactData.total_affected_shipments} shipment${impactData.total_affected_shipments !== 1 ? 's' : ''} are currently exposed to active disruptions.`,
      detail: 'No shipments are at critical or high risk at this time.',
      delay: null,
      impact: impactData.total_estimated_impact,
    }
  }, [impactData, allShipments])

  const summaryLoading = summary.loading
  const isLoading = summaryLoading || disruptions.loading || shipments.loading

  return (
    <div>
      {/* ── KPI Strip ───────────────────────────────────────────────────────── */}
      <div className="kpi-grid">
        <KpiCard
          label="Active Disruptions"
          value={impactData?.total_active_disruptions ?? '—'}
          sub="Events affecting routes"
          variant="critical"
          Icon={Zap}
          loading={summaryLoading}
        />
        <KpiCard
          label="Affected Shipments"
          value={impactData?.total_affected_shipments ?? '—'}
          sub="Across all disruptions"
          variant="high"
          Icon={Package}
          loading={summaryLoading}
        />
        <KpiCard
          label="Critical Shipments"
          value={shipments.loading ? '…' : criticalCount}
          sub="Risk score ≥ 90"
          variant="critical"
          Icon={AlertOctagon}
          loading={shipments.loading && !allShipments.length}
        />
        <KpiCard
          label="High-Risk Shipments"
          value={shipments.loading ? '…' : highRiskCount}
          sub="HIGH or CRITICAL level"
          variant="high"
          Icon={TrendingUp}
          loading={shipments.loading && !allShipments.length}
        />
        <KpiCard
          label="Estimated Exposure"
          value={impactData ? formatCurrency(impactData.total_estimated_impact) : '—'}
          sub="Total financial at risk"
          variant="warning"
          Icon={DollarSign}
          loading={summaryLoading}
        />
      </div>

      {/* ── Health + AI Insight row ─────────────────────────────────────────── */}
      <div className="section-row cols-2-1 mb-5">
        {/* Supply Chain Health */}
        <div className="ai-panel">
          <div className="ai-panel-header">
            <div className="ai-panel-icon">
              <TrendingUp size={14} />
            </div>
            <div>
              <div className="ai-panel-title">Supply Chain Health</div>
              <div className="ai-panel-subtitle">Derived from live disruption and risk data</div>
            </div>
          </div>
          <div className="ai-panel-body">
            {summaryLoading || shipments.loading ? (
              <div style={{ display: 'flex', gap: 'var(--space-5)', alignItems: 'center' }}>
                <div className="skeleton" style={{ width: 110, height: 110, borderRadius: '50%' }} />
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {[1,2,3,4].map(i => <div key={i} className="skeleton skeleton-text" style={{ width: `${60+i*8}%` }} />)}
                </div>
              </div>
            ) : summary.error ? (
              <ErrorState message={summary.error.message} onRetry={summary.refetch} />
            ) : (
              <div className="health-ring-wrap">
                <HealthGauge score={healthScore} />
                <div className="health-factors">
                  {[
                    { label: 'Disruption Severity', val: impactData ? Math.max(0, 100 - (impactData.total_active_disruptions || 0) * 15) : null },
                    { label: 'Shipment Risk',       val: allShipments.length ? Math.max(0, 100 - Math.round((highRiskCount / allShipments.length) * 100)) : null },
                    { label: 'Cargo Exposure',      val: impactData ? Math.max(0, 100 - Math.min(100, (impactData.total_estimated_impact / 10_000_000) * 100)) : null },
                    { label: 'Route Coverage',      val: activeDisruptions.length ? Math.max(0, 100 - activeDisruptions.length * 8) : 95 },
                  ].map(({ label, val }) => (
                    <div key={label} className="health-factor-row">
                      <span className="health-factor-label">{label}</span>
                      <div className="health-factor-bar-track">
                        <div
                          className="health-factor-bar-fill"
                          style={{
                            width: `${val ?? 0}%`,
                            background: val == null ? 'var(--border)' : val >= 70 ? 'var(--risk-low)' : val >= 40 ? 'var(--risk-medium)' : 'var(--risk-high)',
                          }}
                        />
                      </div>
                      <span className="health-factor-val" style={{ color: val == null ? 'var(--text-muted)' : val >= 70 ? 'var(--risk-low)' : val >= 40 ? 'var(--risk-medium)' : 'var(--risk-high)' }}>
                        {val ?? '—'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* AI Insight Panel */}
        <div className="ai-panel">
          <div className="ai-panel-header">
            <div className="ai-panel-icon">
              <Bot size={14} />
            </div>
            <div>
              <div className="ai-panel-title">RouteX AI Intelligence</div>
              <div className="ai-panel-subtitle">Derived from live data</div>
            </div>
          </div>
          <div className="ai-panel-body">
            {summaryLoading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {[1,2,3].map(i => <div key={i} className="skeleton skeleton-text" />)}
              </div>
            ) : !aiInsight ? (
              <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>No active disruptions to analyze.</p>
            ) : (
              <>
                <p className="ai-insight-text">{aiInsight.headline}</p>
                {aiInsight.detail && (
                  <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', marginBottom: 'var(--space-4)', lineHeight: 1.6 }}>
                    {aiInsight.detail}
                  </p>
                )}
                <div className="ai-metric-grid">
                  <div className="ai-metric-item">
                    <div className="ai-metric-label">Avg Delay</div>
                    <div className="ai-metric-value" style={{ fontSize: 'var(--text-lg)', color: aiInsight.delay ? 'var(--risk-medium)' : 'var(--text-muted)' }}>
                      {aiInsight.delay != null ? `${aiInsight.delay}d` : '—'}
                    </div>
                  </div>
                  <div className="ai-metric-item">
                    <div className="ai-metric-label">Exposure</div>
                    <div className="ai-metric-value" style={{ fontSize: 'var(--text-lg)', color: 'var(--risk-high)' }}>
                      <CurrencyDisplay value={aiInsight.impact} />
                    </div>
                  </div>
                  <div className="ai-metric-item">
                    <div className="ai-metric-label">Critical</div>
                    <div className="ai-metric-value" style={{ fontSize: 'var(--text-lg)', color: criticalCount > 0 ? 'var(--risk-critical)' : 'var(--risk-low)' }}>
                      {criticalCount}
                    </div>
                  </div>
                </div>
                <button
                  className="btn btn-ghost btn-sm"
                  style={{ color: 'var(--cyan)', fontSize: 'var(--text-xs)', padding: 0 }}
                  onClick={() => navigate('/copilot')}
                >
                  Ask AI Copilot <ArrowRight size={11} />
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* ── Charts row ──────────────────────────────────────────────────────── */}
      <div className="section-row cols-2 mb-5">
        <SectionCard
          title="Affected Shipments by Disruption"
          headerExtra={
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/disruptions')}>
              View all <ArrowRight size={11} />
            </button>
          }
        >
          {summaryLoading ? <SkeletonChart /> :
           summary.error   ? <ErrorState message={summary.error.message} onRetry={summary.refetch} /> :
           barData.length === 0 ? <EmptyState title="No active disruptions" message="All corridors are clear." /> :
           (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={barData} margin={{ top: 4, right: 8, bottom: 28, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} angle={-20} textAnchor="end" interval={0} />
                <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} width={28} />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Bar dataKey="affected" name="Affected" fill="var(--blue)" radius={[3,3,0,0]} maxBarSize={36} />
              </BarChart>
            </ResponsiveContainer>
           )}
        </SectionCard>

        <SectionCard title="Risk Distribution">
          {summaryLoading ? <SkeletonChart /> :
           summary.error   ? <ErrorState message={summary.error.message} onRetry={summary.refetch} /> :
           pieData.length === 0 ? <EmptyState title="No risk data" message="No affected shipments." /> :
           (
            <>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={44} outerRadius={70} paddingAngle={3} dataKey="value">
                    {pieData.map(entry => (
                      <Cell key={entry.name} fill={RISK_COLORS[entry.name] || '#888'} />
                    ))}
                  </Pie>
                  <Tooltip {...CHART_TOOLTIP_STYLE} />
                  <Legend wrapperStyle={{ fontSize: 11, color: 'var(--text-muted)' }} />
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
      <SectionCard
        title={`Active Disruptions${activeDisruptions.length ? ` (${activeDisruptions.length})` : ''}`}
        headerExtra={
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/disruptions')}>
            Analyze impact <ArrowRight size={11} />
          </button>
        }
        style={{ marginBottom: 'var(--space-5)' }}
        noPad
      >
        {disruptions.loading ? (
          <div style={{ padding: 'var(--space-4) var(--space-5)' }}><SkeletonTable rows={4} cols={6} /></div>
        ) : disruptions.error ? (
          <div style={{ padding: 'var(--space-4)' }}><ErrorState message={disruptions.error.message} onRetry={disruptions.refetch} /></div>
        ) : activeDisruptions.length === 0 ? (
          <EmptyState title="No active disruptions" message="All supply chain corridors are clear." />
        ) : (
          <div className="table-wrapper" style={{ border: 'none', borderRadius: 0 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Location</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Duration</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {activeDisruptions.map(d => (
                  <tr key={d.disruption_id} onClick={() => navigate('/disruptions')}>
                    <td><span className="id-cell">{d.disruption_id}</span></td>
                    <td>{d.location}</td>
                    <td><TypeBadge type={d.type} /></td>
                    <td><RiskBadge level={d.severity} dot /></td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>{d.duration_days}d</td>
                    <td><StatusBadge status={d.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* ── Impact Summary ───────────────────────────────────────────────────── */}
      <SectionCard
        title="Disruption Impact Summary"
        style={{ marginBottom: 'var(--space-5)' }}
        noPad
      >
        {summaryLoading ? (
          <div style={{ padding: 'var(--space-4) var(--space-5)' }}><SkeletonTable rows={4} cols={6} /></div>
        ) : summary.error ? (
          <div style={{ padding: 'var(--space-4)' }}><ErrorState message={summary.error.message} onRetry={summary.refetch} /></div>
        ) : !impactData?.disruptions?.length ? (
          <EmptyState title="No impact data" message="No disruptions are currently affecting shipments." />
        ) : (
          <div className="table-wrapper" style={{ border: 'none', borderRadius: 0 }}>
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
                {impactData.disruptions.map(d => (
                  <tr key={d.disruption_id} onClick={() => navigate('/disruptions')}>
                    <td><span className="id-cell">{d.disruption_id}</span></td>
                    <td>{d.location}</td>
                    <td><TypeBadge type={d.type} /></td>
                    <td><RiskBadge level={d.severity} dot /></td>
                    <td style={{ fontWeight: 700 }}>{d.total_affected}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
                      {d.estimated_delay_days != null ? `${d.estimated_delay_days}d` : '—'}
                    </td>
                    <td><CurrencyDisplay value={d.estimated_impact} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>
    </div>
  )
}
