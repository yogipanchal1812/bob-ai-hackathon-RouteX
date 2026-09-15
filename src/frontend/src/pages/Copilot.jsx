/**
 * RouteX — AI Copilot: Enterprise chat UI with context panel and rich responses.
 *
 * Consumes: POST /api/copilot (Member 3), GET /api/impact-summary
 */

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { Bot, Send, RotateCcw, Sparkles } from 'lucide-react'

import { useApiMutation, useApi } from '../hooks/useApi.js'
import { sendCopilotMessage, fetchImpactSummary } from '../services/api.js'
import { AlertBanner, CurrencyDisplay, RiskBadge } from '../components/common/index.jsx'

const SUGGESTED_PROMPTS = [
  'Which shipments are most affected right now?',
  'What is the impact of the Suez Canal disruption?',
  'Which shipments should we reroute first?',
  'What is the estimated total financial exposure?',
  'What happens if the disruption lasts 5 more days?',
  'Which carrier has the most affected shipments?',
]

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)' }}>
      <div style={{ width: 28, height: 28, borderRadius: 'var(--radius)', background: 'var(--cyan-dim)', border: '1px solid rgba(57,208,216,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        <Bot size={14} color="var(--cyan)" />
      </div>
      <div className="chat-bubble assistant" style={{ padding: 'var(--space-2) var(--space-3)' }}>
        <div className="typing-dots">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
      </div>
    </div>
  )
}

function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`chat-message-wrap ${message.role}`}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)' }}>
        {!isUser && (
          <div style={{ width: 28, height: 28, borderRadius: 'var(--radius)', background: 'var(--cyan-dim)', border: '1px solid rgba(57,208,216,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 2 }}>
            <Bot size={14} color="var(--cyan)" />
          </div>
        )}
        <div className={`chat-bubble ${message.role}${message.isError ? ' error-bubble' : ''}`}>
          {message.content}
        </div>
      </div>
      <div className="chat-meta" style={{ paddingLeft: isUser ? 0 : 40 }}>
        {isUser ? 'You' : 'RouteX AI'} · {message.timestamp}
      </div>
    </div>
  )
}

export default function Copilot() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello. I am the RouteX AI Copilot. I can help you understand disruption impacts, identify at-risk shipments, and recommend operational actions. What would you like to know?',
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
    },
  ])
  const [input, setInput] = useState('')
  const [endpointUnavailable, setEndpointUnavailable] = useState(false)
  const messagesEndRef = useRef(null)

  // Operational context from backend
  const { data: summaryData } = useApi(() => fetchImpactSummary())
  const summary = summaryData?.data

  const { loading: sending, execute: sendMessage } = useApiMutation(sendCopilotMessage)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const handleSend = useCallback(async (text) => {
    const userText = (text || input).trim()
    if (!userText || sending) return

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: userText,
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setEndpointUnavailable(false)

    try {
      const result = await sendMessage({ message: userText })
      const reply = result?.data?.response || result?.response || result?.message
        || result?.data?.content || result?.content
        || (typeof result === 'string' ? result : null)
        || JSON.stringify(result)
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: reply,
          timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
        },
      ])
    } catch (err) {
      const isServiceDown = err.status === 404 || err.status === 405 || err.status === null
      setEndpointUnavailable(isServiceDown)
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: isServiceDown
            ? 'The AI Copilot service (POST /api/copilot) is not yet available. This interface will connect automatically once Member 3 deploys the endpoint.'
            : `Error: ${err.message || 'Unable to reach the AI Copilot service.'}`,
          timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
          isError: true,
        },
      ])
    }
  }, [input, sending, sendMessage])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClear = () => {
    setMessages([{
      id: 'cleared',
      role: 'assistant',
      content: 'Conversation cleared. How can I assist you?',
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
    }])
    setEndpointUnavailable(false)
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 'var(--space-4)', height: 'calc(100vh - var(--topbar-height) - var(--space-8) - var(--space-8))' }}>
      {/* ── Chat area ──────────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', flexDirection: 'column', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 'var(--space-3) var(--space-5)', borderBottom: '1px solid var(--border)', background: 'rgba(57,208,216,0.03)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Sparkles size={14} color="var(--cyan)" />
            <span style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--cyan)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              AI Copilot
            </span>
            {endpointUnavailable && (
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--risk-medium)', background: 'var(--risk-medium-dim)', border: '1px solid var(--risk-medium-border)', borderRadius: 99, padding: '1px 8px' }}>
                Service Pending
              </span>
            )}
          </div>
          <button className="btn btn-ghost btn-sm" onClick={handleClear} aria-label="Clear conversation">
            <RotateCcw size={12} /> Clear
          </button>
        </div>

        {/* Messages */}
        <div
          className="chat-messages"
          aria-live="polite"
          aria-label="Conversation"
          style={{ flex: 1 }}
        >
          {messages.map(msg => <ChatMessage key={msg.id} message={msg} />)}
          {sending && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="chat-input-row">
          <input
            type="text"
            placeholder="Ask about disruptions, shipment risks, rerouting recommendations…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={sending}
            aria-label="Message to AI Copilot"
            maxLength={500}
          />
          <button
            className="btn btn-primary"
            onClick={() => handleSend()}
            disabled={sending || !input.trim()}
            aria-label="Send message"
          >
            <Send size={13} />
            {sending ? 'Sending…' : 'Send'}
          </button>
        </div>
      </div>

      {/* ── Right panel ────────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', overflow: 'hidden' }}>
        {/* Operational context */}
        <div className="context-panel">
          <div className="context-panel-header">Operational Context</div>
          <div className="context-metric">
            <span className="context-metric-label">Active Disruptions</span>
            <span className="context-metric-value" style={{ color: 'var(--risk-critical)' }}>
              {summary?.total_active_disruptions ?? '—'}
            </span>
          </div>
          <div className="context-metric">
            <span className="context-metric-label">Affected Shipments</span>
            <span className="context-metric-value" style={{ color: 'var(--risk-high)' }}>
              {summary?.total_affected_shipments ?? '—'}
            </span>
          </div>
          <div className="context-metric">
            <span className="context-metric-label">Critical Risk</span>
            <span className="context-metric-value" style={{ color: 'var(--risk-critical)' }}>
              {summary?.risk_distribution?.critical_risk ?? '—'}
            </span>
          </div>
          <div className="context-metric">
            <span className="context-metric-label">High Risk</span>
            <span className="context-metric-value" style={{ color: 'var(--risk-high)' }}>
              {summary?.risk_distribution?.high_risk ?? '—'}
            </span>
          </div>
          <div className="context-metric">
            <span className="context-metric-label">Est. Exposure</span>
            <span className="context-metric-value">
              <CurrencyDisplay value={summary?.total_estimated_impact} />
            </span>
          </div>
        </div>

        {/* Suggested prompts */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', overflow: 'hidden', flex: 1 }}>
          <div className="context-panel-header">Suggested Queries</div>
          <div style={{ padding: 'var(--space-3)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            {SUGGESTED_PROMPTS.map((prompt, i) => (
              <button
                key={i}
                className="btn btn-secondary"
                style={{ textAlign: 'left', justifyContent: 'flex-start', whiteSpace: 'normal', lineHeight: 1.4, fontSize: 'var(--text-xs)' }}
                onClick={() => handleSend(prompt)}
                disabled={sending}
              >
                {prompt}
              </button>
            ))}
          </div>
          <div style={{ padding: 'var(--space-3) var(--space-4)', borderTop: '1px solid var(--border)', fontSize: 'var(--text-xs)', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Powered by IBM Bob (Member 3). This UI does not generate synthetic responses.
          </div>
        </div>
      </div>
    </div>
  )
}
