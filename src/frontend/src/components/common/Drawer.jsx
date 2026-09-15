/**
 * RouteX — Drawer component for detail panels.
 */
import React, { useEffect } from 'react'
import { X } from 'lucide-react'

export default function Drawer({ isOpen, onClose, title, children, width }) {
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <>
      <div
        className="drawer-overlay"
        onClick={onClose}
        aria-hidden="true"
      />
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        style={width ? { width } : undefined}
      >
        <div className="drawer-header">
          <h2>{title}</h2>
          <button
            className="btn btn-ghost btn-icon"
            onClick={onClose}
            aria-label="Close panel"
          >
            <X size={16} />
          </button>
        </div>
        <div className="drawer-body">
          {children}
        </div>
      </aside>
    </>
  )
}
