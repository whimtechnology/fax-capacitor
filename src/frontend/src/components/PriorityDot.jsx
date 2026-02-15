import { useState, useRef, useEffect } from 'react'
import { PRIORITIES } from '../constants'

export default function PriorityDot({ priority, urgencyIndicators = [] }) {
  const [showTooltip, setShowTooltip] = useState(false)
  const dotRef = useRef(null)
  const tooltipRef = useRef(null)

  const config = PRIORITIES[priority] || PRIORITIES.none
  const hasIndicators = urgencyIndicators && urgencyIndicators.length > 0

  return (
    <div className="relative flex items-center justify-center">
      <div
        ref={dotRef}
        className="w-2.5 h-2.5 rounded-full cursor-default"
        style={{
          backgroundColor: config.color,
          boxShadow: hasIndicators
            ? `0 0 0 2px #fff, 0 0 0 4px ${config.color}44`
            : 'none'
        }}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      />

      {showTooltip && (
        <div
          ref={tooltipRef}
          className="absolute left-full ml-2 z-50 bg-gray-800 text-white text-xs rounded px-2.5 py-1.5 shadow-lg"
          style={{ whiteSpace: 'nowrap' }}
        >
          <div className="font-semibold">{config.label} Priority</div>
          {hasIndicators && (
            <div className="mt-1 space-y-0.5">
              {urgencyIndicators.map((indicator, idx) => (
                <div
                  key={idx}
                  className="text-red-300 uppercase text-[10px] font-medium"
                >
                  {indicator}
                </div>
              ))}
            </div>
          )}
          <div
            className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-r-gray-800 border-y-transparent border-l-transparent"
          />
        </div>
      )}
    </div>
  )
}
