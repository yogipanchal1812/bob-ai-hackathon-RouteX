/**
 * RouteX Frontend — AI Copilot page.
 *
 * Consumes: POST /api/copilot (Member 3 — may not yet be available)
 * Provides a professional chat interface for AI-assisted decision support.
 * Does NOT generate fake AI responses.
 * Shows a graceful error state when the service is unavailable.
 */

import React, { useState, useRef, useEffect } from 'react'

import { useApiMutation } from '../hooks/useApi.js'
import { sendCopilotMessage } from '../services/api.js'
import { AlertBanner, EmptyState, SectionCard, PageHeader } from '../components/common/index.jsx'

const SUGGESTED_PROMPTS = [
  'Which shipments are most at risk right now?',
  'What is the impact of the Suez Canal disruption?',
  'Which carrier has the most affected shipments?',
  'Recommend rerouting options for CRITICAL shipments.',
  'What is the estimated total financial exposure today?',
]

function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
      <div className={`chat-bubble ${message.role}`}>
        {message.content}
      </div>
      <div className="chat-meta" style={{ textAlign: isUser ? 'right' : 'left' }}>
        {isUser ? 'You' : 'AI Copilot'} · {message.timestamp}
      </div>
    </div>
  )
}

export default function Copilot() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello. I am the ChainGuard AI Copilot. Ask me about your current disruptions, shipment risks, or recommended actions.',
      timestamp: new Date().toLocaleTimeString(),
    },
  ])
  const [input, setInput] = useState('')
  const [endpointUnavailable, setEndpointUnavailable] = useState(false)
  const messagesEndRef = useRef(null)

  const { loading: sending, execute: sendMessage } = useApiMutation(sendCopilotMessage)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (text) => {
    const userText = (text || input).trim()
    if (!userText || sending) return

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: userText,
      timestamp: new Date().toLocaleTimeString(),
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setEndpointUnavailable(false)

    try {
      const result = await sendMessage({ message: userText })
      const reply = result?.data?.response || result?.response || result?.message || JSON.stringify(result)
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: reply,
          timestamp: new Date().toLocaleTimeString(),
        },
      ])
    } catch (err) {
      if (err.status === 404 || err.status === 405 || err.status === null) {
        setEndpointUnavailable(true)
        setMessages(prev => [
          ...prev,
          {
            id: Date.now() + 1,
            role: 'assistant',
            content: 'The AI Copilot service (POST /api/copilot) is not yet available. This interface is ready and will connect once Member 3 deploys the endpoint.',
            timestamp: new Date().toLocaleTimeString(),
            isError: true,
          },
        ])
      } else {
        setMessages(prev => [
          ...prev,
          {
            id: Date.now() + 1,
            role: 'assistant',
            content: `Error: ${err.message || 'Unable to reach the AI Copilot service.'}`,
            timestamp: new Date().toLocaleTimeString(),
            isError: true,
          },
        ])
      }
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClear = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Conversation cleared. How can I help you?',
        timestamp: new Date().toLocaleTimeString(),
      },
    ])
    setEndpointUnavailable(false)
  }

  return (
    <div>
      <PageHeader
        title="AI Copilot"
        subtitle="IBM Bob-powered decision support for supply chain operations"
        actions={
          <button className="btn btn-secondary btn-sm" onClick={handleClear}>
            Clear conversation
          </button>
        }
      />

      {endpointUnavailable && (
        <AlertBanner type="warning">
          <strong>AI service unavailable.</strong> POST /api/copilot is provided by Member 3 (IBM Bob integration).
          Messages will connect once the endpoint is deployed.
        </AlertBanner>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 'var(--space-4)', height: 'calc(100vh - 220px)', minHeight: 400 }}>
        {/* ── Chat area ──────────────────────────────────────────────────────── */}
        <SectionCard style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
          {/* Messages */}
          <div
            className="chat-messages"
            style={{ flex: 1, overflowY: 'auto' }}
            aria-live="polite"
            aria-label="Conversation"
          >
            {messages.map(msg => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {sending && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>
                <div style={{ display: 'flex', gap: 3 }}>
                  <span style={{ animation: 'pulse 1s ease-in-out infinite', animationDelay: '0ms' }}>●</span>
                  <span style={{ animation: 'pulse 1s ease-in-out infinite', animationDelay: '200ms' }}>●</span>
                  <span style={{ animation: 'pulse 1s ease-in-out infinite', animationDelay: '400ms' }}>●</span>
                </div>
                <span>AI Copilot is thinking…</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input row */}
          <div className="chat-input-row">
            <input
              type="text"
              placeholder="Ask about disruptions, risks, recommendations…"
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
              {sending ? '…' : 'Send'}
            </button>
          </div>
        </SectionCard>

        {/* ── Suggested prompts sidebar ──────────────────────────────────────── */}
        <SectionCard title="Suggested Queries">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            {SUGGESTED_PROMPTS.map((prompt, i) => (
              <button
                key={i}
                className="btn btn-secondary"
                style={{ textAlign: 'left', justifyContent: 'flex-start', whiteSpace: 'normal', lineHeight: 1.4 }}
                onClick={() => handleSend(prompt)}
                disabled={sending}
              >
                {prompt}
              </button>
            ))}
          </div>

          <div
            style={{
              marginTop: 'var(--space-5)',
              paddingTop: 'var(--space-4)',
              borderTop: '1px solid var(--border)',
              fontSize: 'var(--text-xs)',
              color: 'var(--text-muted)',
              lineHeight: 1.5,
            }}
          >
            <p style={{ fontWeight: 600, marginBottom: 'var(--space-1)', color: 'var(--text-secondary)' }}>IBM Bob Integration</p>
            <p>Responses are generated by IBM Bob (Member 3). This UI does not generate fake responses.</p>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
