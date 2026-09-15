/**
 * RouteX — Toast notification container.
 */
import React from 'react'
import { CheckCircle, AlertTriangle, Info, XCircle, X } from 'lucide-react'
import { useAppContext } from '../../context/AppContext.jsx'

const ICONS = {
  success: <CheckCircle size={15} />,
  error:   <XCircle size={15} />,
  warning: <AlertTriangle size={15} />,
  info:    <Info size={15} />,
}

export default function ToastContainer() {
  const { toasts, removeToast } = useAppContext()
  if (toasts.length === 0) return null
  return (
    <div className="toast-container" role="region" aria-live="polite" aria-label="Notifications">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type}`} role="alert">
          {ICONS[t.type] || ICONS.info}
          <span className="toast-msg">{t.message}</span>
          <button
            style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', opacity: 0.6, padding: 0 }}
            onClick={() => removeToast(t.id)}
            aria-label="Dismiss notification"
          >
            <X size={13} />
          </button>
        </div>
      ))}
    </div>
  )
}
