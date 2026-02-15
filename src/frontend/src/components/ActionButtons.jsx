import Tooltip from './Tooltip'

export default function ActionButtons({ onReview, onFlag, onDismiss, isLoading }) {
  return (
    <div className="flex gap-2">
      <Tooltip content="Mark as reviewed and handled" position="top">
        <button
          onClick={onReview}
          disabled={isLoading}
          className="action-button flex-1 px-4 py-2 rounded-lg border-2 border-green-600 text-green-600 font-medium text-sm hover:bg-green-600 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          &#10003; Reviewed
        </button>
      </Tooltip>

      <Tooltip content="Flag for follow-up — find under Flagged filter" position="top">
        <button
          onClick={onFlag}
          disabled={isLoading}
          className="action-button flex-1 px-4 py-2 rounded-lg border-2 border-amber-600 text-amber-600 font-medium text-sm hover:bg-amber-600 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          &#128681; Flag
        </button>
      </Tooltip>

      <Tooltip content="Dismiss — removes from active queue" position="top">
        <button
          onClick={onDismiss}
          disabled={isLoading}
          className="action-button flex-1 px-4 py-2 rounded-lg border-2 border-gray-500 text-gray-500 font-medium text-sm hover:bg-gray-500 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          &#10005; Dismiss
        </button>
      </Tooltip>
    </div>
  )
}
