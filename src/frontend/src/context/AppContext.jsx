/**
 * RouteX — App context for shared state (sidebar collapse, toasts).
 */
import React, { createContext, useContext, useState, useCallback } from 'react'

const AppCtx = createContext(null)

export function AppProvider({ children }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [toasts, setToasts] = useState([])

  const toggleSidebar = useCallback(() => setSidebarCollapsed(v => !v), [])

  const addToast = useCallback((message, type = 'info', duration = 3500) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, type }])
    if (duration > 0) {
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), duration)
    }
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <AppCtx.Provider value={{ sidebarCollapsed, toggleSidebar, toasts, addToast, removeToast }}>
      {children}
    </AppCtx.Provider>
  )
}

export function useAppContext() {
  const ctx = useContext(AppCtx)
  if (!ctx) throw new Error('useAppContext must be used within AppProvider')
  return ctx
}
