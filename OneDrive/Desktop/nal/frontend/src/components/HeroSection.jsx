export default function HeroSection({ onTriage, loading, hasFetched }) {
  return (
    <section className="hero">
      <div className="hero-tag">
        <span>🤖</span> AI-Powered · LangChain + Gemini
      </div>
      <h1>Your Unified<br />Priority Inbox</h1>
      <p>
        NexusFlow fetches your Gmail and Slack messages, runs them through
        an AI triage engine, and delivers a single ranked inbox — so you always
        know what demands your attention.
      </p>

      <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
        <button
          id="triage-btn"
          className="btn btn-primary btn-lg"
          onClick={onTriage}
          disabled={loading}
        >
          {loading
            ? <><span className="spin">⟳</span> Analyzing Messages...</>
            : <><span>🔍</span> {hasFetched ? 'Re-run Triage' : 'Run AI Triage'}</>
          }
        </button>

        {!hasFetched && (
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="btn btn-ghost btn-lg"
          >
            📖 API Docs
          </a>
        )}
      </div>

      {loading && (
        <div style={{ marginTop: 24 }}>
          <div className="loader-dots">
            <div className="dot" />
            <div className="dot" />
            <div className="dot" />
          </div>
          <p style={{ color: 'var(--text-muted)', marginTop: 12, fontSize: 13 }}>
            Fetching Gmail · Slack · Scoring with Gemini AI...
          </p>
        </div>
      )}
    </section>
  )
}
