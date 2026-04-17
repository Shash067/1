const CATEGORIES = [
  { id: 'All',                    label: 'All',        icon: '📬', tabClass: '' },
  { id: 'Urgent/Action Required', label: 'Urgent',     icon: '🔴', tabClass: 'urgent-tab' },
  { id: 'Informational',          label: 'Info',       icon: '💡', tabClass: 'info-tab' },
  { id: 'Ignore/Newsletter',      label: 'Ignore',     icon: '🗑️', tabClass: 'ignore-tab' },
]

export default function FilterBar({
  messages, activeCategory, setActiveCategory, activeSource, setActiveSource
}) {
  const countFor = (id) =>
    id === 'All'
      ? messages.length
      : messages.filter(m => m.category === id).length

  return (
    <div className="tab-bar">
      {CATEGORIES.map(cat => (
        <button
          key={cat.id}
          className={`tab ${activeCategory === cat.id ? `active ${cat.tabClass}` : ''}`}
          onClick={() => setActiveCategory(cat.id)}
        >
          <span>{cat.icon}</span>
          {cat.label}
          <span className="tab-count">{countFor(cat.id)}</span>
        </button>
      ))}

      <div className="source-filter">
        {['All', 'gmail', 'slack'].map(src => (
          <button
            key={src}
            className={`src-btn ${activeSource === src ? `active-${src}` : ''}`}
            onClick={() => setActiveSource(src)}
          >
            {src === 'gmail' && '✉️'}
            {src === 'slack' && '💬'}
            {src === 'All'   && '🔀'}
            {src === 'All' ? 'All Sources' : src.charAt(0).toUpperCase() + src.slice(1)}
          </button>
        ))}
      </div>
    </div>
  )
}
