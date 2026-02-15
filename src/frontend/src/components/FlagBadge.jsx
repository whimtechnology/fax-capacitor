import { FLAGS } from '../constants'

export default function FlagBadge({ flag }) {
  const config = FLAGS[flag]

  if (!config) {
    return null
  }

  return (
    <span
      className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase border"
      style={{
        color: config.textColor,
        backgroundColor: config.bgColor,
        borderColor: config.borderColor
      }}
    >
      {config.label}
    </span>
  )
}

export function FlagList({ flags }) {
  if (!flags || flags.length === 0) {
    return <span className="text-gray-300">&mdash;</span>
  }

  return (
    <div className="flex flex-col gap-0.5">
      {flags.map((flag, idx) => (
        <FlagBadge key={idx} flag={flag} />
      ))}
    </div>
  )
}
