import { CONFIDENCE_THRESHOLDS } from '../constants'

export default function ConfidenceBadge({ confidence }) {
  const percentage = Math.round(confidence * 100)

  let color
  if (confidence >= CONFIDENCE_THRESHOLDS.high) {
    color = '#16A34A' // green
  } else if (confidence >= CONFIDENCE_THRESHOLDS.medium) {
    color = '#CA8A04' // yellow
  } else {
    color = '#DC2626' // red
  }

  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono font-medium"
      style={{
        color: color,
        backgroundColor: `${color}11`
      }}
    >
      {percentage}%
    </span>
  )
}
