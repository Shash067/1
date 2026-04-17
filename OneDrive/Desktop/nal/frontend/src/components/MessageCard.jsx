import { useState } from 'react'

function getCategoryClass(category) {
  if (category === 'Urgent/Action Required') return 'urgent'
  if (category === 'Informational')          return 'informational'
  return 'ignore'
}

function getScoreClass(score) {
  if (score >= 7) return 'high'
  if (score >= 4) return 'mid'
  return 'low'
}

function formatTime(isoString) {
  try {
    const d = new Date(isoString)
    const now = new Date()
    const diffMs = now - d
    const diffMin = Math.floor(diffMs / 60000)
    const diffHr  = Math.floor(diffMs / 3600000)

    if (diffMin < 1)  return 'just now'
    if (diffMin < 60) return `${diffMin}m ago`
    if (diffHr < 24)  return `${diffHr}h ago`
    return d.toLocaleDateString()
  } catch {
    return isoString
  }
}

function getCategoryEmoji(category) {
  if (category === 'Urgent/Action Required') return '🔴'
  if (category === 'Informational')          return '💡'
  return '🗑️'
}

function getTagClass(tag, source) {
  if (tag === source) return source
  if (tag === 'urgent') return 'urgent'
  if (['informational', 'system', 'colleague'].includes(tag)) return 'info'
  return 'default'
}

export default function MessageCard({ message: msg, index }) {
  const [expanded, setExpanded] = useState(false)

  const catClass   = getCategoryClass(msg.category)
  const scoreClass = getScoreClass(msg.urgency_score)

  return (
    <div
      className={`message-card ${catClass}`}
      onClick={() => setExpanded(p => !p)}
      role="button"
      tabIndex={0}
      id={`msg-card-${index}`}
      style={{ animationDelay: `${index * 0.05}s` }}
      onKeyDown={e => e.key === 'Enter' && setExpanded(p => !p)}
    >
      {/* ── Header ── */}
      <div className="card-header">
        <div className="card-meta">
          {/* Source icon */}
          <div className={`source-icon ${msg.source}`}>
            {msg.source === 'gmail' ? '✉' : '💬'}
          </div>

          {/* Sender */}
          <div className="sender-info">
            <span className="sender-name">{msg.sender}</span>
            <span className="sender-role">{msg.sender_role}</span>
          </div>
        </div>

        {/* Urgency score ring */}
        <div className="urgency-badge">
          <div className={`score-ring ${scoreClass}`} title={`Urgency: ${msg.urgency_score}/10`}>
            {msg.urgency_score}
          </div>
          <span
            className={`category-pill ${catClass}`}
            style={{ display: 'none' }}
          >
            {getCategoryEmoji(msg.category)}
          </span>
        </div>
      </div>

      {/* ── Subject ── */}
      <div className="card-subject">{msg.subject}</div>

      {/* ── TL;DR ── */}
      <div className="card-tldr">
        <span className="tldr-label">TL;DR</span>
        <span className="tldr-text">{msg.tldr}</span>
      </div>

      {/* ── Expanded body ── */}
      {expanded && (
        <div className="card-body-expanded" onClick={e => e.stopPropagation()}>
          {msg.body}
        </div>
      )}

      {/* ── Tags ── */}
      <div className="card-tags">
        <span className={`category-pill ${catClass}`}>
          {getCategoryEmoji(msg.category)} {msg.category}
        </span>
        {(msg.tags || []).map(tag => (
          <span key={tag} className={`tag ${getTagClass(tag, msg.source)}`}>{tag}</span>
        ))}
      </div>

      {/* ── Footer ── */}
      <div className="card-footer">
        <span className="card-timestamp">🕐 {formatTime(msg.timestamp)}</span>
        {msg.channel && (
          <span className="card-channel">{msg.channel}</span>
        )}
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          {expanded ? '▲ Collapse' : '▼ Show full message'}
        </span>
      </div>
    </div>
  )
}
