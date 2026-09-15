/**
 * RouteX — Fleet Operations dashboard.
 * Consumes: GET /api/fleet (Member 4 — may not yet be available)
 */

import React from 'react'
import { Ship, AlertCircle, RefreshCw } from 'lucide-react'

import { useApi } from '../hooks/useApi.js'
import { fetchFleet } from '../services/api.js'
import {
  SkeletonKpiCard, ErrorState, EmptyState, SectionCard, AlertBanner, StatusBadge,
} from '../components/common/index.jsx'

function FleetKpi({ label, value, variant, loading }) {
  if (loading) return <SkeletonKpiCard />
  return (
    <div className={`kpi-card${variant ? ` kpi-${variant}` : ''}`}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value ?? '—'}</div>
    </div>
  )
}

function FleetCard({ vehicle }) {
  const statusColor = {
    AVAILABLE: 'var(--risk-low)', IN_TRANSIT: 'var(--status-transit)',
    IDLE: 'var(--text-muted)', MAINTENANCE: 'var(--risk-medium)',
  }[vehicle.status] || 'var(--text-muted)'

  return (
    <div className="card" style={{ borderLeft: `3px solid ${statusColor}` }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 'var(--text-base)', color: 'var(--text-bright)' }}>
          {vehicle.vehicle_id}
        </span>
        {vehicle.status && <StatusBadge status={vehicle.status} />}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)', fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
        {vehicle.carrier_id && <span>Carrier: <span style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{vehicle.carrier_id}</span></span>}
        {vehicle.type && <span>Type: <span style={{ color: 'var(--text-primary)' }}>{vehicle.type}</span></span>}
        {vehicle.capacity != null && <span>Capacity: <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{vehicle.capacity}</span></span>}
        {vehicle.utilization != null && <span>Utilization: <span style={{ color: vehicle.utilization > 80 ? 'var(--risk-high)' : 'var(--risk-low)', fontWeight: 700 }}>{vehicle.utilization}%</span></span>}
        {vehicle.current_location && (
          <span style={{ gridColumn: '1 / -1' }}>Location: <span style={{ color: 'var(--text-primary)' }}>{vehicle.current_location}</span></span>
        )}
      </div>
    </div>
  )
}

export default function Fleet() {
  const { data, loading, error, refetch } = useApi(() => fetchFleet())
  const fleet = data?.data || []

  // Compute KPIs from actual fleet data
  const available    = fleet.filter(v => v.status === 'AVAILABLE').length
  const inTransit    = fleet.filter(v => v.status === 'IN_TRANSIT').length
  const idle         = fleet.filter(v => v.status === 'IDLE').length
  const maintenance  = fleet.filter(v => v.status === 'MAINTENANCE').length
  const avgUtil      = fleet.length
    ? Math.round(fleet.filter(v => v.utilization != null).reduce((acc, v) => acc + v.utilization, 0) / (fleet.filter(v => v.utilization != null).length || 1))
    : null

  const isEndpointMissing = error?.status === 404 || error?.status === 405

  return (
    <div>
      {/* KPIs */}
      <div className="kpi-grid">
        <FleetKpi label="Total Fleet" value={fleet.length || '—'} variant="blue" loading={loading} />
        <FleetKpi label="Available" value={fleet.length ? available : '—'} variant="ok" loading={loading} />
        <FleetKpi label="In Transit" value={fleet.length ? inTransit : '—'} variant="blue" loading={loading} />
        <FleetKpi label="Idle" value={fleet.length ? idle : '—'} loading={loading} />
        <FleetKpi label="Avg Utilization" value={avgUtil != null ? `${avgUtil}%` : '—'} variant={avgUtil > 80 ? 'high' : 'ok'} loading={loading} />
      </div>

      {/* Fleet body */}
      <SectionCard
        title={fleet.length ? `Fleet (${fleet.length} vehicles)` : 'Fleet'}
        headerExtra={
          <button className="btn btn-secondary btn-sm" onClick={refetch} disabled={loading}>
            <RefreshCw size={12} /> {loading ? 'Loading…' : 'Refresh'}
          </button>
        }
      >
        {loading ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 'var(--space-4)' }}>
            {Array(6).fill(0).map((_, i) => <SkeletonKpiCard key={i} />)}
          </div>
        ) : error ? (
          <>
            {isEndpointMissing && (
              <AlertBanner type="warning">
                <strong>Fleet endpoint not yet available.</strong> GET /api/fleet is provided by Member 4.
                This interface is ready and will display fleet data as soon as the endpoint is live.
              </AlertBanner>
            )}
            <EmptyState
              title="Fleet data unavailable"
              message={isEndpointMissing
                ? 'The /api/fleet endpoint has not been implemented yet.'
                : error.message || 'Unable to connect to the fleet service.'}
            >
              <button className="btn btn-secondary btn-sm" onClick={refetch} style={{ marginTop: 'var(--space-3)' }}>
                Retry
              </button>
            </EmptyState>
          </>
        ) : fleet.length === 0 ? (
          <EmptyState title="No fleet data" message="No vehicles are currently registered." />
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 'var(--space-4)' }}>
            {fleet.map((vehicle, i) => (
              <FleetCard key={vehicle.vehicle_id || i} vehicle={vehicle} />
            ))}
          </div>
        )}
      </SectionCard>
    </div>
  )
}
