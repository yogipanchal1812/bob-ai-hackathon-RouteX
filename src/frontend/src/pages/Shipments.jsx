/**
 * RouteX Frontend — Shipments page.
 *
 * Consumes: GET /api/shipments, GET /api/shipments/:id
 * Displays: Filterable shipment table + selected shipment detail panel.
 */

import React, { useState, useMemo } from 'react'

import { useApi } from '../hooks/useApi.js'
import { fetchShipments, fetchShipment } from '../services/api.js'
import {
  LoadingState, ErrorState, EmptyState, SectionCard,
  RiskBadge, StatusBadge, CurrencyDisplay, RiskScoreBar, PageHeader, DetailField,
} from '../components/common/index.jsx'
import { formatDate } from '../utils/format.js'

const STATUS_OPTIONS = ['', 'IN_TRANSIT', 'DELAYED', 'DELIVERED', 'CANCELLED']

export default function Shipments() {
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedId, setSelectedId] = useState(null)

  // ── Fetch list ────────────────────────────────────────────────────────────────
  const { data, loading, error, refetch } = useApi(
    () => fetchShipments(statusFilter ? { status: statusFilter } : {}),
    [statusFilter]
  )
  const shipments = data?.data || []

  // ── Fetch detail ──────────────────────────────────────────────────────────────
  const detail = useApi(
    () => selectedId ? fetchShipment(selectedId) : Promise.resolve(null),
    [selectedId],
    { immediate: !!selectedId }
  )
  const shipmentDetail = detail.data?.data

  // ── Derived ───────────────────────────────────────────────────────────────────
  const sortedShipments = useMemo(() => {
    return [...shipments].sort((a, b) => {
      // Sort by risk (CRITICAL > HIGH > MEDIUM > LOW), then by shipment_id
      const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }
      const ra = order[a.risk_level] ?? 4
      const rb = order[b.risk_level] ?? 4
      if (ra !== rb) return ra - rb
      return a.shipment_id.localeCompare(b.shipment_id)
    })
  }, [shipments])

  const handleSelect = (shipmentId) => {
    setSelectedId(prev => prev === shipmentId ? null : shipmentId)
  }

  return (
    <div>
      <PageHeader
        title="Shipments"
        subtitle={`${shipments.length} shipment${shipments.length !== 1 ? 's' : ''} loaded`}
        actions={
          <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <select
                value={statusFilter}
                onChange={e => { setStatusFilter(e.target.value); setSelectedId(null) }}
                style={{ minWidth: 140 }}
                aria-label="Filter by status"
              >
                <option value="">All Statuses</option>
                {STATUS_OPTIONS.filter(Boolean).map(s => (
                  <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
                ))}
              </select>
            </div>
            <button
              className="btn btn-secondary btn-sm"
              onClick={refetch}
              disabled={loading}
            >
              {loading ? 'Loading…' : '↻ Refresh'}
            </button>
          </div>
        }
      />

      <SectionCard>
        {loading ? (
          <LoadingState message="Loading shipments…" />
        ) : error ? (
          <ErrorState message={error.message} onRetry={refetch} />
        ) : sortedShipments.length === 0 ? (
          <EmptyState
            title="No shipments found"
            message={statusFilter ? `No shipments with status "${statusFilter}".` : 'No shipment data available.'}
            icon="📦"
          />
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Shipment ID</th>
                  <th>Origin</th>
                  <th>Destination</th>
                  <th>Route</th>
                  <th>Carrier</th>
                  <th>Cargo Type</th>
                  <th>Value</th>
                  <th>Priority</th>
                  <th>ETA</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {sortedShipments.map(s => (
                  <tr
                    key={s.shipment_id}
                    onClick={() => handleSelect(s.shipment_id)}
                    className={selectedId === s.shipment_id ? 'selected' : ''}
                    role="button"
                    tabIndex={0}
                    onKeyDown={e => e.key === 'Enter' && handleSelect(s.shipment_id)}
                    aria-pressed={selectedId === s.shipment_id}
                  >
                    <td><span className="id-cell">{s.shipment_id}</span></td>
                    <td>{s.origin}</td>
                    <td>{s.destination}</td>
                    <td><span className="id-cell">{s.route_id}</span></td>
                    <td><span className="id-cell">{s.carrier_id}</span></td>
                    <td>{s.cargo_type}</td>
                    <td><CurrencyDisplay value={s.cargo_value} /></td>
                    <td><RiskBadge level={s.priority} /></td>
                    <td>{formatDate(s.eta)}</td>
                    <td><StatusBadge status={s.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* ── Detail Panel ─────────────────────────────────────────────────────── */}
      {selectedId && (
        <div className="detail-panel">
          <h3>
            Shipment Detail — <span className="text-mono" style={{ fontSize: 'var(--text-base)' }}>{selectedId}</span>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setSelectedId(null)}
              aria-label="Close detail panel"
            >
              ✕ Close
            </button>
          </h3>

          {detail.loading ? (
            <LoadingState message="Loading shipment details…" />
          ) : detail.error ? (
            <ErrorState message={detail.error.message} onRetry={detail.refetch} />
          ) : shipmentDetail ? (
            <div>
              <div className="detail-grid">
                <DetailField label="Shipment ID" value={shipmentDetail.shipment_id} mono />
                <DetailField label="Origin" value={shipmentDetail.origin} />
                <DetailField label="Destination" value={shipmentDetail.destination} />
                <DetailField label="Route ID" value={shipmentDetail.route_id} mono />
                <DetailField label="Carrier ID" value={shipmentDetail.carrier_id} mono />
                <DetailField label="Cargo Type" value={shipmentDetail.cargo_type} />
                <DetailField
                  label="Cargo Value"
                  value={<CurrencyDisplay value={shipmentDetail.cargo_value} />}
                />
                <DetailField label="Priority" value={<RiskBadge level={shipmentDetail.priority} />} />
                <DetailField label="ETA" value={formatDate(shipmentDetail.eta)} />
                <DetailField label="Status" value={<StatusBadge status={shipmentDetail.status} />} />
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}
