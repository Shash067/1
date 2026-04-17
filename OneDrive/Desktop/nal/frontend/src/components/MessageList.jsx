import MessageCard from './MessageCard'

export default function MessageList({ messages, loading }) {
  if (loading && messages.length === 0) {
    return (
      <div className="loading-overlay">
        <div className="loader-dots">
          <div className="dot" />
          <div className="dot" />
          <div className="dot" />
        </div>
        <p className="loading-text">AI is analyzing your messages...</p>
      </div>
    )
  }

  if (messages.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📭</div>
        <h3>No messages in this filter</h3>
        <p>Try selecting a different category or source above.</p>
      </div>
    )
  }

  return (
    <div className="messages-container">
      {messages.map((msg, i) => (
        <MessageCard key={msg.id} message={msg} index={i} />
      ))}
    </div>
  )
}
