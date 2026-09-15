/**
 * RouteX Frontend — API Service Layer
 *
 * All calls to the backend go through this file.
 * Endpoint names must match the shared API contract exactly.
 * Never invent responses — surface errors to callers.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * Core fetch wrapper — handles JSON parsing and consistent error shape.
 * @param {string} path
 * @param {RequestInit} options
 * @returns {Promise<any>}
 */
async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  let response
  try {
    response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
  } catch (networkErr) {
    throw new ApiError('Network error — backend may be unavailable.', null, networkErr)
  }

  let body
  try {
    body = await response.json()
  } catch {
    throw new ApiError(`Server returned non-JSON response (${response.status})`, response.status)
  }

  if (!response.ok) {
    const message = body?.error || body?.detail || body?.message || `Request failed (${response.status})`
    throw new ApiError(message, response.status)
  }

  return body
}

// ── Custom error class ──────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(message, status = null, cause = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.cause = cause
  }
}

// ── Endpoints ───────────────────────────────────────────────────────────────

/**
 * GET /api/health
 */
export async function fetchHealth() {
  return request('/api/health')
}

/**
 * GET /api/shipments
 * @param {{ status?: string }} [filters]
 */
export async function fetchShipments(filters = {}) {
  const params = new URLSearchParams()
  if (filters.status) params.set('status', filters.status)
  const qs = params.toString() ? `?${params}` : ''
  return request(`/api/shipments${qs}`)
}

/**
 * GET /api/shipments/:id
 * @param {string} shipmentId
 */
export async function fetchShipment(shipmentId) {
  return request(`/api/shipments/${encodeURIComponent(shipmentId)}`)
}

/**
 * GET /api/disruptions
 * @param {{ status?: string }} [filters]
 */
export async function fetchDisruptions(filters = {}) {
  const params = new URLSearchParams()
  if (filters.status) params.set('status', filters.status)
  const qs = params.toString() ? `?${params}` : ''
  return request(`/api/disruptions${qs}`)
}

/**
 * GET /api/disruptions/:id
 * @param {string} disruptionId
 */
export async function fetchDisruption(disruptionId) {
  return request(`/api/disruptions/${encodeURIComponent(disruptionId)}`)
}

/**
 * GET /api/routes
 */
export async function fetchRoutes() {
  return request('/api/routes')
}

/**
 * POST /api/analyze-disruption
 * @param {string} disruptionId
 */
export async function analyzeDisruption(disruptionId) {
  return request('/api/analyze-disruption', {
    method: 'POST',
    body: JSON.stringify({ disruption_id: disruptionId }),
  })
}

/**
 * GET /api/impact-summary
 */
export async function fetchImpactSummary() {
  return request('/api/impact-summary')
}

/**
 * GET /api/fleet  (Member 4 — may not yet be available)
 */
export async function fetchFleet() {
  return request('/api/fleet')
}

/**
 * POST /api/what-if  (Member 4 — may not yet be available)
 * @param {{ disruption_id: string, duration_days: number, severity: string }} payload
 */
export async function runWhatIf(payload) {
  return request('/api/what-if', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/**
 * POST /api/copilot  (Member 3 — may not yet be available)
 * @param {{ message: string, context?: object }} payload
 */
export async function sendCopilotMessage(payload) {
  return request('/api/copilot', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/**
 * POST /api/recommendation  (Member 3 — may not yet be available)
 * @param {object} payload
 */
export async function fetchRecommendation(payload) {
  return request('/api/recommendation', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
