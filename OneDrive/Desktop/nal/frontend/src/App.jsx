import { useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import HeroSection from './components/HeroSection'
import StatsGrid from './components/StatsGrid'
import FilterBar from './components/FilterBar'
import MessageList from './components/MessageList'
import Toast from './components/Toast'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [stats, setStats]       = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [toast, setToast]       = useState(null)
  const [activeCategory, setActiveCategory] = useState('All')
  const [activeSource, setActiveSource]     = useState('All')
  const [hasFetched, setHasFetched]         = useState(false)

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3500)
  }

  const handleTriage = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/triage`, { method: 'POST' })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setMessages(data.messages)
      setStats(data.stats)
      setHasFetched(true)
      showToast(`✅ Triaged ${data.stats.total} messages — ${data.stats.urgent_count} urgent!`)
    } catch (err) {
      setError(err.message)
      showToast(`❌ ${err.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }, [])

  const filteredMessages = messages.filter(msg => {
    const catMatch = activeCategory === 'All' || msg.category === activeCategory
    const srcMatch = activeSource === 'All' || msg.source === activeSource
    return catMatch && srcMatch
  })

  const urgentCount = messages.filter(m => m.category === 'Urgent/Action Required').length

  return (
    <div className="app-shell">
      <div className="bg-grid" />
      <Navbar urgentCount={urgentCount} />

      <main className="main-content">
        <HeroSection onTriage={handleTriage} loading={loading} hasFetched={hasFetched} />

        {stats && <StatsGrid stats={stats} />}

        {hasFetched && (
          <>
            <div className="divider" />
            <div className="section-header">
              <h2 className="section-title">
                <span>📥</span> Priority Inbox
                {loading && <span className="spin" style={{ fontSize: 16 }}>⟳</span>}
              </h2>
              <button
                className="btn btn-ghost"
                onClick={handleTriage}
                disabled={loading}
              >
                {loading ? <span className="spin">⟳</span> : '🔄'} Refresh
              </button>
            </div>

            <FilterBar
              messages={messages}
              activeCategory={activeCategory}
              setActiveCategory={setActiveCategory}
              activeSource={activeSource}
              setActiveSource={setActiveSource}
            />

            <MessageList messages={filteredMessages} loading={loading} />
          </>
        )}
      </main>

      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  )
}

export default App
