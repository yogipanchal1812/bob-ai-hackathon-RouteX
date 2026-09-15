/**
 * RouteX Frontend — Shared utility functions.
 * No business logic — display helpers only.
 */

/**
 * Format a numeric value as USD currency display.
 * @param {number} value
 * @returns {string}
 */
export function formatCurrency(value) {
  if (value == null || isNaN(value)) return '—'
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`
  return `$${value.toFixed(2)}`
}

/**
 * Format an ISO date string to a readable display.
 * @param {string} isoDate
 * @returns {string}
 */
export function formatDate(isoDate) {
  if (!isoDate) return '—'
  try {
    const d = new Date(isoDate)
    if (isNaN(d.getTime())) return isoDate
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return isoDate
  }
}

/**
 * Truncate a string to maxLength, appending ellipsis if needed.
 * @param {string} str
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(str, maxLength = 40) {
  if (!str) return '—'
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength - 1) + '…'
}

/**
 * Returns the CSS class name for a risk level badge.
 * Validated against the team contract: LOW | MEDIUM | HIGH | CRITICAL
 * @param {string} level
 * @returns {string}
 */
export function riskBadgeClass(level) {
  const valid = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
  if (!level || !valid.includes(level.toUpperCase())) return 'badge badge-MEDIUM'
  return `badge badge-${level.toUpperCase()}`
}

/**
 * Returns the CSS class name for a status badge (disruption status).
 * @param {string} status
 * @returns {string}
 */
export function statusBadgeClass(status) {
  if (!status) return 'badge'
  return `badge badge-${status.toUpperCase()}`
}

/**
 * Determine risk level from a numeric score per team contract.
 * 0–39 LOW · 40–69 MEDIUM · 70–89 HIGH · 90–100 CRITICAL
 * @param {number} score
 * @returns {string}
 */
export function riskLevelFromScore(score) {
  if (score == null || isNaN(score)) return 'UNKNOWN'
  if (score >= 90) return 'CRITICAL'
  if (score >= 70) return 'HIGH'
  if (score >= 40) return 'MEDIUM'
  return 'LOW'
}

/**
 * Return a CSS color variable string for a risk level.
 * @param {string} level
 * @returns {string}
 */
export function riskColor(level) {
  const map = {
    LOW: 'var(--risk-low)',
    MEDIUM: 'var(--risk-medium)',
    HIGH: 'var(--risk-high)',
    CRITICAL: 'var(--risk-critical)',
  }
  return map[level?.toUpperCase()] || 'var(--text-secondary)'
}

/**
 * Format a disruption type string for display.
 * @param {string} type
 * @returns {string}
 */
export function formatDisruptionType(type) {
  if (!type) return '—'
  return type.replace(/_/g, ' ')
}

/**
 * Safely access a nested value, returning fallback on undefined/null.
 * @param {any} obj
 * @param {string} path  dot-separated key path
 * @param {any} fallback
 * @returns {any}
 */
export function safeGet(obj, path, fallback = '—') {
  const val = path.split('.').reduce((acc, k) => (acc != null ? acc[k] : undefined), obj)
  return val != null && val !== '' ? val : fallback
}

/**
 * Check if an API error is a "not found" (404).
 * @param {Error} err
 * @returns {boolean}
 */
export function isNotFound(err) {
  return err?.status === 404
}

/**
 * Map severity string to a display icon.
 * @param {string} severity
 * @returns {string}
 */
export function severityIcon(severity) {
  const map = {
    CRITICAL: '🔴',
    HIGH: '🟠',
    MEDIUM: '🟡',
    LOW: '🟢',
  }
  return map[severity?.toUpperCase()] || '⚪'
}
