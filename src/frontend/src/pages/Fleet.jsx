/**
 * RouteX Frontend — Fleet page.
 *
 * Consumes: GET /api/fleet (Member 4 — may not yet be available)
 * Creates a clean API service interface expecting the agreed contract.
 * Does NOT implement fleet backend logic.
 */

import React from 'react'

import { useApi } from '../hooks/useApi.js'
import { fetchFleet } from '../services/api.js'
import {
  LoadingState, ErrorState, EmptyState, SectionCard, AlertBanner,
  StatusBadge, PageHeader,
} from '../components/common/index.jsx'

// ── Expected fleet contract (for documentation / graceful empty state) ─────────
// GET /api/fleet → { success: true, count: N, data: [{ vehicle_id, carrier_id, ... }] }

function FleetCard({ vehicle }) {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span className="text-mono" style={{ fontWeight: 700, fontSize: 'var(--text-base)' }}>
          {vehicle.vehicle_id}
        </span>
        {vehicle.status && <StatusBadge status={vehicle.status} />}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)', fontSize: 'var(--text-sm)' }}>
        {vehicle.carrier_id && (
          <div>
            <span className="text-secondary">Carrier: </span>
            <span className="text-mono">{vehicle.carrier_id}</span>
          </div>
        )}
        {vehicle.type && (
          <div>
            <span className="text-secondary">Type: </span>
            <span>{vehicle.type}</span>
          </div>
        )}
        {vehicle.capacity != null && (
          <div>
            <span className="text-secondary">Capacity: </span>
            <span>{vehicle.capacity}</span>
          </div>
        )}
        {vehicle.utilization != null && (
          <div>
            <span className="text-secondary">Utilization: </span>
            <span style={{ fontWeight: 600 }}>{vehicle.utilization}%</span>
          </div>
        )}
        {vehicle.current_location && (
          <div style={{ gridColumn: '1 / -1' }}>
            <span className="text-secondary">Location: </span>
            <span>{vehicle.current_location}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Fleet() {
  const { data, loading, error, refetch } = useApi(() => fetchFleet())
  const fleet = data?.data || []

  return (
    <div>
      <PageHeader
        title="Fleet"
        subtitle="Vehicle capacity and carrier availability overview"
        actions={
          <button className="btn btn-secondary btn-sm" onClick={refetch} disabled={loading}>
            {loading ? 'Loading…' : '↻ Refresh'}
          </button>
        }
      />

      {/* Availability notice */}
      {!loading && error && (
        <AlertBanner type="warning">
          <strong>Fleet endpoint not yet available.</strong> The fleet API (GET /api/fleet) is provided by Member 4.
          This interface is ready and will display fleet data as soon as the endpoint is live.
        </AlertBanner>
      )}

      <SectionCard>
        {loading ? (
          <LoadingState message="Loading fleet data…" />
        ) : error ? (
          <div>
            <EmptyState
              title="Fleet data unavailable"
              message={
                error.status === 404
                  ? 'The /api/fleet endpoint has not been implemented yet. This UI is ready to consume it.'
                  : error.message || 'Unable to connect to the fleet service.'
              }
              icon="🚢"
            />
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: 'var(--space-4)' }}>
              <button className="btn btn-secondary btn-sm" onClick={refetch}>
                Retry
              </button>
            </div>
          </div>
        ) : fleet.length === 0 ? (
          <EmptyState title="No fleet data" message="No vehicles are currently registered." icon="🚢" />
        ) : (
          <div>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
              {fleet.length} vehicle{fleet.length !== 1 ? 's' : ''} found
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 'var(--space-4)' }}>
              {fleet.map((vehicle, i) => (
                <FleetCard key={vehicle.vehicle_id || i} vehicle={vehicle} />
              ))}
            </div>
          </div>
        )}
      </SectionCard>
    </div>
  )
}
