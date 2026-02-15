import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import StatsBar from './components/StatsBar'
import FilterBar from './components/FilterBar'
import DocumentQueue from './components/DocumentQueue'
import DocumentDetail from './components/DocumentDetail'
import UploadZone from './components/UploadZone'
import { getStats, getDocuments } from './api'
import { DEFAULT_FILTERS } from './constants'

function buildApiFilters(filters, statFilter) {
  const apiParams = {}

  // Handle type filter
  if (filters.type) {
    apiParams.document_type = filters.type
  }

  // Handle stat card filter (overrides status dropdown when active)
  if (statFilter) {
    switch (statFilter) {
      case 'total':
        // Show all
        break
      case 'unreviewed':
        apiParams.status = 'classified'
        break
      case 'urgent':
        apiParams.priority = 'high,critical'
        break
      case 'reviewed':
        apiParams.status = 'reviewed'
        break
      case 'flagged':
        apiParams.status = 'flagged'
        break
    }
  } else {
    // Handle status dropdown filter
    switch (filters.status) {
      case 'unreviewed':
        apiParams.status = 'classified'
        break
      case 'urgent':
        apiParams.priority = 'high,critical'
        break
      case 'new':
        apiParams.status = 'classified'
        break
      case 'flagged':
        apiParams.status = 'flagged'
        break
      case 'reviewed':
        apiParams.status = 'reviewed'
        break
      case 'dismissed':
        apiParams.status = 'dismissed'
        break
      // '' = all statuses, no filter
    }
  }

  return apiParams
}

export default function App() {
  const [stats, setStats] = useState(null)
  const [documents, setDocuments] = useState([])
  const [selectedDocumentId, setSelectedDocumentId] = useState(null)
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [statFilter, setStatFilter] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const [statsData, docsData] = await Promise.all([
        getStats(),
        getDocuments(buildApiFilters(filters, statFilter))
      ])

      setStats(statsData)
      setDocuments(docsData)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [filters, statFilter])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleStatCardClick = (key) => {
    if (statFilter === key) {
      // Clicking active card resets to default
      setStatFilter(null)
      setFilters(DEFAULT_FILTERS)
    } else {
      setStatFilter(key)
      // Reset dropdown filters when using stat cards
      setFilters({ type: '', status: '' })
    }
    setSelectedDocumentId(null)
  }

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
    setStatFilter(null) // Clear stat card selection when using dropdowns
    setSelectedDocumentId(null)
  }

  const handleUploadComplete = () => {
    fetchData()
  }

  const handleAction = () => {
    fetchData()
  }

  const selectedDocument = documents.find(d => d.id === selectedDocumentId)

  // Compute active filter for stat cards
  const activeStatFilter = statFilter || (
    filters.status === 'unreviewed' && !filters.type ? 'unreviewed' : null
  )

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <svg
            className="w-16 h-16 mx-auto text-red-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <StatsBar
        stats={stats}
        activeFilter={activeStatFilter}
        onFilterClick={handleStatCardClick}
      />
      <UploadZone onUploadComplete={handleUploadComplete} />
      <FilterBar
        filters={filters}
        onFilterChange={handleFilterChange}
        documentCount={documents.length}
      />

      <div className="flex">
        <div className={`flex-1 p-6 ${selectedDocument ? 'pr-0' : ''}`}>
          <DocumentQueue
            documents={documents}
            selectedId={selectedDocumentId}
            onSelect={setSelectedDocumentId}
            isLoading={isLoading}
          />
        </div>

        {selectedDocument && (
          <DocumentDetail
            document={selectedDocument}
            onClose={() => setSelectedDocumentId(null)}
            onAction={handleAction}
          />
        )}
      </div>
    </div>
  )
}
