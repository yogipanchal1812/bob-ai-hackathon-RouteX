/**
 * RouteX Frontend — useApi hook
 *
 * Generic hook for making API calls with loading / error / data state.
 * Does NOT implement backend logic — only manages fetch state.
 */

import { useState, useEffect, useCallback, useRef } from 'react'

/**
 * @param {Function} apiFn  - async function that returns data
 * @param {Array} deps      - dependency array to re-trigger
 * @param {object} options
 * @param {boolean} options.immediate - trigger immediately (default true)
 * @returns {{ data, loading, error, refetch }}
 */
export function useApi(apiFn, deps = [], options = {}) {
  const { immediate = true } = options
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => { mountedRef.current = false }
  }, [])

  const execute = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiFn()
      if (mountedRef.current) {
        setData(result)
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err)
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false)
      }
    }
  }, deps) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (immediate) execute()
  }, [execute, immediate])

  return { data, loading, error, refetch: execute }
}

/**
 * @param {Function} apiFn  - async function that accepts args and returns data
 * @returns {{ data, loading, error, execute }}
 *
 * Usage: const { execute, loading, data, error } = useApiMutation(analyzeDisruption)
 *        await execute('D001')
 */
export function useApiMutation(apiFn) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => { mountedRef.current = false }
  }, [])

  const execute = useCallback(async (...args) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiFn(...args)
      if (mountedRef.current) setData(result)
      return result
    } catch (err) {
      if (mountedRef.current) setError(err)
      throw err
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }, [apiFn])

  return { data, loading, error, execute }
}
