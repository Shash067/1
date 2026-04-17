export default function Navbar({ urgentCount }) {
  return (
    <nav className="navbar">
      <a href="/" className="nav-logo">
        <div className="logo-icon">⚡</div>
        <div>
          <div className="logo-text">NexusFlow</div>
          <span className="logo-sub">Communication Triage</span>
        </div>
      </a>

      <div className="nav-right">
        {urgentCount > 0 && (
          <span className="nav-badge pulsing">
            🔴 {urgentCount} Urgent
          </span>
        )}
        <div style={{ fontSize: 13, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', display: 'inline-block', boxShadow: '0 0 8px #10b981' }} />
          API Live
        </div>
      </div>
    </nav>
  )
}
