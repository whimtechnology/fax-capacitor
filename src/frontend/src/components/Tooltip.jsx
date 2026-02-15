import { useState, useRef, useEffect } from 'react'

export default function Tooltip({ children, content, position = 'top', className = '' }) {
  const [isVisible, setIsVisible] = useState(false)
  const [tooltipPosition, setTooltipPosition] = useState(position)
  const triggerRef = useRef(null)
  const tooltipRef = useRef(null)

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect()
      const tooltipRect = tooltipRef.current.getBoundingClientRect()

      // Check if tooltip would go off screen at top
      if (position === 'top' && triggerRect.top < tooltipRect.height + 10) {
        setTooltipPosition('bottom')
      } else if (position === 'bottom' && window.innerHeight - triggerRect.bottom < tooltipRect.height + 10) {
        setTooltipPosition('top')
      } else {
        setTooltipPosition(position)
      }
    }
  }, [isVisible, position])

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2'
  }

  const arrowClasses = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-gray-800 border-x-transparent border-b-transparent',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-gray-800 border-x-transparent border-t-transparent',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-gray-800 border-y-transparent border-r-transparent',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-gray-800 border-y-transparent border-l-transparent'
  }

  if (!content) {
    return children
  }

  return (
    <div
      ref={triggerRef}
      className={`relative inline-flex ${className}`}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          ref={tooltipRef}
          className={`absolute z-50 ${positionClasses[tooltipPosition]}`}
        >
          <div className="bg-gray-800 text-white text-xs rounded px-2 py-1.5 shadow-lg whitespace-nowrap">
            {content}
          </div>
          <div
            className={`absolute border-4 ${arrowClasses[tooltipPosition]}`}
          />
        </div>
      )}
    </div>
  )
}
