import { STAT_CARDS } from '../constants'

export default function StatsBar({ stats, activeFilter, onFilterClick }) {
  const getStatValue = (key) => {
    if (!stats) return '—'

    switch (key) {
      case 'total':
        return stats.total_documents ?? '—'
      case 'unreviewed':
        return stats.counts_by_status?.classified ?? 0
      case 'urgent': {
        const high = stats.counts_by_priority?.high ?? 0
        const critical = stats.counts_by_priority?.critical ?? 0
        return high + critical
      }
      case 'reviewed':
        return stats.counts_by_status?.reviewed ?? 0
      case 'flagged':
        return stats.counts_by_status?.flagged ?? 0
      case 'confidence':
        if (stats.avg_confidence !== null && stats.avg_confidence !== undefined) {
          return `${Math.round(stats.avg_confidence * 100)}%`
        }
        return '—'
      default:
        return '—'
    }
  }

  const isActive = (key) => {
    return activeFilter === key
  }

  return (
    <div className="grid grid-cols-6 gap-4 px-6 py-4">
      {STAT_CARDS.map(card => {
        const active = isActive(card.key)
        const clickable = card.clickable

        return (
          <div
            key={card.key}
            onClick={() => clickable && onFilterClick(card.key)}
            className={`
              bg-white rounded-lg p-4 border
              ${clickable ? 'stat-card-clickable' : 'cursor-default'}
              ${active
                ? 'border-2'
                : 'border-gray-200'
              }
            `}
            style={{
              borderColor: active ? `${card.color}40` : undefined,
              backgroundColor: active ? `${card.color}08` : undefined
            }}
          >
            <div className="text-sm text-gray-500 font-medium mb-1">
              {card.label}
            </div>
            <div
              className="text-2xl font-bold font-mono"
              style={{ color: card.color }}
            >
              {getStatValue(card.key)}
            </div>
          </div>
        )
      })}
    </div>
  )
}
