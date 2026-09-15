/**
 * RouteX — Shipments: Enterprise shipment management with search, filtering, drawer.
 *
 * Consumes: GET /api/shipments, GET /api/shipments/:id
 */

import React, { useState, useMemo, useCallback } from 'react'
import { Search, Filter, SlidersHorizontal } from 'lucide-react'

import { useApi } from '../hooks/useApi.js'
import { fetchShipments, fetchShipment } from '../services/api.js'
import {
  SkeletonTable, ErrorState, EmptyState, SectionCard,
  RiskBadge, StatusBadge, CurrencyDisplay, RiskScoreBar, DetailField,
} from '../components/common/index.jsx'
import Drawer from '../components/common/Drawer.jsx'
import { formatDate } from '../utils/format.js'

const STATUS_FILTERS   = ['ALL', 'IN_TRANSIT', 'DELAYED', 'DELIVERED', 'CANCELLED']
const PRIORITY_FILTERS = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
const RISK_ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }

export default function Shipments() {
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [priorityFilter, setPriorityFilter] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedId, setSelectedId] = useState(null)

  // ── Fetch list ────────────────────────────────────────────────────────────────
  const { data, loading, error, refetch } = useApi(() => fetchShipments())
  const shipments = data?.data || []

  // ── Fetch detail ──────────────────────────────────────────────────────────────
  const detail = useApi(
    () => selectedId ? fetchShipment(selectedId) : Promise.resolve(null),
    [selectedId],
    { immediate: !!selectedId }
  )
  const shipmentDetail = detail.data?.data

  // ── Filter + sort ─────────────────────────────────────────────────────────────
  const filtered = useMemo(() => {
    let list = shipments
    if (statusFilter !== 'ALL') list = list.filter(s => s.status === statusFilter)
    if (priorityFilter !== 'ALL') list = list.filter(s => s.priority === priorityFilter)
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      list = list.filter(s =>
        s.shipment_id.toLowerCase().includes(q) ||
        s.origin.toLowerCase().includes(q) ||
        s.destination.toLowerCase().includes(q) ||
        s.carrier_id.toLowerCase().includes(q) ||
        s.cargo_type.toLowerCase().includes(q)
      )
    }
    return [...list].sort((a, b) => {
      const ra = RISK_ORDER[a.risk_level] ?? 4
      const rb = RISK_ORDER[b.risk_level] ?? 4
      if (ra !== rb) return ra - rb
      return a.shipment_id.localeCompare(b.shipment_id)
    })
  }, [shipments, statusFilter, priorityFilter, searchQuery])

  const handleSelect = useCallback((id) => {
    setSelectedId(prev => prev === id ? null : id)
  }, [])

  return (
    <div>
      {/* ── Controls ─────────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 'var(--space-3)', marginBottom: 'var(--space-5)', flexWrap: 'wrap', alignItems: 'center' }}>
        <div className="search-box" style={{ flex: '1 1 220px', maxWidth: 320 }}>
          <span className="search-box-icon"><Search size={13} /></span>
          <input
            type="search"
            placeholder="Search ID, origin, destination, carrier…"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            aria-label="Search shipments"
          />
        </div>

        <div className="filter-row" style={{ margin: 0 }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginRight: 4 }}>
            <Filter size={11} style={{ display: 'inline' }} /> Status:
          </span>
          {STATUS_FILTERS.map(s => (
            <button key={s} className={`filter-chip${statusFilter === s ? ' active' : ''}`} onClick={() => setStatusFilter(s)}>
              {s.replace(/_/g, ' ')}
            </button>
          ))}
        </div>

        <div className="filter-row" style={{ margin: 0 }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginRight: 4 }}>
            <SlidersHorizontal size={11} style={{ display: 'inline' }} /> Priority:
          </span>
          {PRIORITY_FILTERS.map(s => (
            <button
              key={s}
              className={`filter-chip${priorityFilter === s ? ` active chip-${s}` : ''}`}
              onClick={() => setPriorityFilter(s)}
            >
              {s}
            </button>
          ))}
        </div>

        <button className="btn btn-secondary btn-sm" onClick={refetch} disabled={loading}>
          {loading ? 'Loading…' : '↻'}
        </button>
      </div>

      {/* ── Count line ───────────────────────────────────────────────────────── */}
      {!loading && !error && (
        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginBottom: 'var(--space-3)' }}>
          Showing {filtered.length} of {shipments.length} shipments
          {selectedId && ' · Click a row to deselect'}
        </div>
      )}

      {/* ── Table ────────────────────────────────────────────────────────────── */}
      <SectionCard noPad>
        {loading ? (
          <div style={{ padding: 'var(--space-4)' }}><SkeletonTable rows={8} cols={8} /></div>
        ) : error ? (
          <div style={{ padding: 'var(--space-4)' }}><ErrorState message={error.message} onRetry={refetch} /></div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title="No shipments found"
            message={shipments.length === 0 ? 'No shipment data available.' : 'No shipments match the current filters.'}
            icon="📦"
          />
        ) : (
          <div className="table-wrapper" style={{ border: 'none', borderRadius: 0 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Shipment ID</th>
                  <th>Origin</th>
                  <th>Destination</th>
                  <th>Carrier</th>
                  <th>Cargo Type</th>
                  <th>Value</th>
                  <th>Priority</th>
                  <th>ETA</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(s => (
                  <tr
                    key={s.shipment_id}
                    onClick={() => handleSelect(s.shipment_id)}
                    className={selectedId === s.shipment_id ? 'selected' : ''}
                    tabIndex={0}
                    onKeyDown={e => e.key === 'Enter' && handleSelect(s.shipment_id)}
                    role="button"
                    aria-pressed={selectedId === s.shipment_id}
                  >
                    <td><span className="id-cell">{s.shipment_id}</span></td>
                    <td>{s.origin}</td>
                    <td>{s.destination}</td>
                    <td><span className="id-cell">{s.carrier_id}</span></td>
                    <td>{s.cargo_type}</td>
                    <td><CurrencyDisplay value={s.cargo_value} /></td>
                    <td><RiskBadge level={s.priority} /></td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>{formatDate(s.eta)}</td>
                    <td><StatusBadge status={s.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* ── Detail Drawer ─────────────────────────────────────────────────────── */}
      <Drawer
        isOpen={!!selectedId}
        onClose={() => setSelectedId(null)}
        title={selectedId ? `Shipment ${selectedId}` : ''}
      >
        {selectedId && (
          <ShipmentDrawerContent
            shipmentId={selectedId}
            loading={detail.loading}
            error={detail.error}
            data={shipmentDetail}
            onRetry={detail.refetch}
          />
        )}
      </Drawer>
    </div>
  )
}

// ── Shipment drawer content ───────────────────────────────────────────────────

function ShipmentDrawerContent({ shipmentId, loading, error, data: s, onRetry }) {
  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {Array(8).fill(0).map((_, i) => (
          <div key={i} className="skeleton skeleton-text" style={{ width: `${50 + (i % 3) * 20}%` }} />
        ))}
      </div>
    )
  }
  if (error) return <ErrorState message={error.message} onRetry={onRetry} />
  if (!s) return null

  return (
    <>
      {/* Shipment Info */}
      <div>
        <div className="drawer-section-title">Shipment Details</div>
        <div className="detail-grid">
          <DetailField label="Shipment ID" value={s.shipment_id} mono />
          <DetailField label="Status" value={<StatusBadge status={s.status} />} />
          <DetailField label="Origin" value={s.origin} />
          <DetailField label="Destination" value={s.destination} />
          <DetailField label="Route ID" value={s.route_id} mono />
          <DetailField label="Carrier ID" value={s.carrier_id} mono />
          <DetailField label="Cargo Type" value={s.cargo_type} />
          <DetailField label="Cargo Value" value={<CurrencyDisplay value={s.cargo_value} />} />
          <DetailField label="Priority" value={<RiskBadge level={s.priority} />} />
          <DetailField label="ETA" value={formatDate(s.eta)} />
        </div>
      </div>

      {/* Risk insight — if fields are present */}
      {(s.risk_score != null || s.risk_level) && (
        <div>
          <div className="drawer-section-title">Risk Intelligence</div>
          <div className="detail-grid">
            {s.risk_score != null && (
              <DetailField
                label="Risk Score"
                value={<RiskScoreBar score={s.risk_score} level={s.risk_level} />}
              />
            )}
            {s.risk_level && <DetailField label="Risk Level" value={<RiskBadge level={s.risk_level} dot />} />}
          </div>
        </div>
      )}
    </>
  )
}
