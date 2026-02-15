import { TYPE_FILTER_OPTIONS, STATUS_FILTER_OPTIONS, DEFAULT_FILTERS } from '../constants'

export default function FilterBar({ filters, onFilterChange, documentCount }) {
  const isDefaultFilter = filters.type === DEFAULT_FILTERS.type &&
                          filters.status === DEFAULT_FILTERS.status

  const handleTypeChange = (e) => {
    onFilterChange({ ...filters, type: e.target.value })
  }

  const handleStatusChange = (e) => {
    onFilterChange({ ...filters, status: e.target.value })
  }

  const handleClearFilters = () => {
    onFilterChange({ ...DEFAULT_FILTERS })
  }

  return (
    <div className="flex items-center justify-between px-6 py-3 bg-white border-b border-gray-200">
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-gray-600">Filter:</span>

        <select
          value={filters.type}
          onChange={handleTypeChange}
          className="text-sm border border-gray-300 rounded-md px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {TYPE_FILTER_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        <select
          value={filters.status}
          onChange={handleStatusChange}
          className="text-sm border border-gray-300 rounded-md px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {STATUS_FILTER_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {!isDefaultFilter && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <span className="text-lg leading-none">&times;</span>
            Clear Filters
          </button>
        )}
      </div>

      <div className="text-sm text-gray-500">
        {documentCount} {documentCount === 1 ? 'document' : 'documents'}
      </div>
    </div>
  )
}
