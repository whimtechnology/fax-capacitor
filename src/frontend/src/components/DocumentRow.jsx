import PriorityDot from './PriorityDot'
import ConfidenceBadge from './ConfidenceBadge'
import { FlagList } from './FlagBadge'
import { DOCUMENT_TYPES, STATUSES } from '../constants'

function toTitleCase(name) {
  if (!name) return name
  return name.replace(/\b\w+/g, word =>
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  )
}

function formatSmartDate(dateStr) {
  if (!dateStr) return '—'

  // Backend sends UTC timestamps without 'Z' suffix, so append it
  const utcDateStr = dateStr.endsWith('Z') ? dateStr : `${dateStr}Z`
  const date = new Date(utcDateStr)

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  // Compare using local date parts (date is now correctly converted to local)
  const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const timeStr = date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })

  if (dateOnly.getTime() === today.getTime()) {
    return timeStr
  } else if (dateOnly.getTime() === yesterday.getTime()) {
    return `Yesterday, ${timeStr}`
  } else {
    const monthDay = date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
    return `${monthDay}, ${timeStr}`
  }
}

function TypeBadge({ type }) {
  const config = DOCUMENT_TYPES[type] || DOCUMENT_TYPES.other

  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
      style={{
        color: config.color,
        backgroundColor: `${config.color}11`
      }}
    >
      {config.label}
    </span>
  )
}

function StatusBadge({ status }) {
  const config = STATUSES[status] || STATUSES.classified

  return (
    <span
      className="inline-flex items-center text-xs font-semibold uppercase"
      style={{ color: config.color }}
    >
      {config.emoji && <span className="mr-0.5">&#128681;</span>}
      {config.label}
    </span>
  )
}

export default function DocumentRow({ document, isSelected, onClick }) {
  const patientName = document.extracted_fields?.patient_name
  const facility = document.extracted_fields?.sending_facility
  const urgencyIndicators = document.extracted_fields?.urgency_indicators || []

  return (
    <tr
      onClick={onClick}
      className={`document-row border-b border-gray-100 ${isSelected ? 'selected' : ''}`}
    >
      <td className="px-3 py-3">
        <PriorityDot
          priority={document.priority}
          urgencyIndicators={urgencyIndicators}
        />
      </td>
      <td className="px-3 py-3">
        <TypeBadge type={document.document_type} />
      </td>
      <td className="px-3 py-3">
        <FlagList flags={document.flags} />
      </td>
      <td className="px-3 py-3">
        {patientName ? (
          <span className="text-sm text-gray-900">{toTitleCase(patientName)}</span>
        ) : (
          <span className="text-sm text-gray-400 italic">No patient</span>
        )}
      </td>
      <td className="px-3 py-3">
        {facility ? (
          <span className="text-sm text-gray-600 truncate max-w-[200px] block">
            {facility}
          </span>
        ) : (
          <span className="text-sm text-gray-400 italic">Unknown</span>
        )}
      </td>
      <td className="px-3 py-3">
        <ConfidenceBadge confidence={document.confidence} />
      </td>
      <td className="px-3 py-3">
        <span className="text-sm text-gray-600 font-mono">
          {formatSmartDate(document.upload_time)}
        </span>
      </td>
      <td className="px-3 py-3">
        <StatusBadge status={document.status} />
      </td>
    </tr>
  )
}
