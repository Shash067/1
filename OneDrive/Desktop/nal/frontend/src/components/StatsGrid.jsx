export default function StatsGrid({ stats }) {
  if (!stats) return null

  const items = [
    { label: 'Total Messages',   value: stats.total,               className: 'total',  sub: 'Fetched this run'   },
    { label: 'Urgent',           value: stats.urgent_count,        className: 'urgent', sub: 'Needs your action'  },
    { label: 'Informational',    value: stats.informational_count, className: 'info',   sub: 'Read when free'     },
    { label: 'Ignored',          value: stats.ignore_count,        className: 'ignore', sub: 'Newsletters & noise'},
    { label: 'Avg AI Score',     value: `${stats.avg_urgency_score}/10`, className: 'score', sub: 'Urgency level'  },
    { label: 'Gmail',            value: stats.gmail_count,         className: 'total',  sub: 'Email messages'     },
    { label: 'Slack',            value: stats.slack_count,         className: 'info',   sub: 'Channel messages'   },
  ]

  return (
    <div className="stats-grid">
      {items.map((item, i) => (
        <div className="stat-card" key={i} style={{ animationDelay: `${i * 0.05}s` }}>
          <div className="stat-label">{item.label}</div>
          <div className={`stat-value ${item.className}`}>{item.value}</div>
          <div className="stat-sub">{item.sub}</div>
        </div>
      ))}
    </div>
  )
}
