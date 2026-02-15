import { useState } from 'react'
import DocumentRow from './DocumentRow'
import { SORT_COLUMNS, DEFAULT_SORT, PRIORITIES } from '../constants'

function SortHeader({ column, currentSort, onSort }) {
  if (!column.sortable) {
    return (
      <th className={`px-3 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider ${column.width}`}>
        {column.label}
      </th>
    )
  }

  const isActive = currentSort.key === column.key
  const isAsc = currentSort.order === 'asc'

  const handleClick = () => {
    if (isActive) {
      onSort({ key: column.key, order: isAsc ? 'desc' : 'asc' })
    } else {
      onSort({ key: column.key, order: 'asc' })
    }
  }

  return (
    <th
      className={`px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider cursor-pointer select-none ${column.width}`}
      onClick={handleClick}
    >
      <span className={`flex items-center gap-1 ${isActive ? 'text-blue-700' : 'text-gray-500'}`}>
        {column.label}
        <span className={`sort-indicator ${isActive ? 'active' : ''}`}>
          {isActive ? (isAsc ? '▲' : '▼') : '⇅'}
        </span>
      </span>
    </th>
  )
}

function sortDocuments(documents, sort) {
  const sorted = [...documents]

  sorted.sort((a, b) => {
    let aVal, bVal

    switch (sort.key) {
      case 'priority': {
        aVal = PRIORITIES[a.priority]?.order ?? 99
        bVal = PRIORITIES[b.priority]?.order ?? 99
        break
      }
      case 'document_type':
        aVal = a.document_type || ''
        bVal = b.document_type || ''
        break
      case 'patient_name':
        aVal = a.extracted_fields?.patient_name || ''
        bVal = b.extracted_fields?.patient_name || ''
        break
      case 'sending_facility':
        aVal = a.extracted_fields?.sending_facility || ''
        bVal = b.extracted_fields?.sending_facility || ''
        break
      case 'confidence':
        aVal = a.confidence ?? 0
        bVal = b.confidence ?? 0
        break
      case 'upload_time':
        aVal = new Date(a.upload_time).getTime()
        bVal = new Date(b.upload_time).getTime()
        break
      default:
        return 0
    }

    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }

    if (aVal < bVal) return sort.order === 'asc' ? -1 : 1
    if (aVal > bVal) return sort.order === 'asc' ? 1 : -1
    return 0
  })

  return sorted
}

export default function DocumentQueue({ documents, selectedId, onSelect, isLoading }) {
  const [sort, setSort] = useState(DEFAULT_SORT)

  const sortedDocuments = sortDocuments(documents, sort)

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="p-8 text-center text-gray-400">
          <svg className="animate-spin h-8 w-8 mx-auto mb-2" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Loading documents...
        </div>
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="p-8 text-center text-gray-400">
          <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          No documents match the current filters
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            {SORT_COLUMNS.map(col => (
              <SortHeader
                key={col.key}
                column={col}
                currentSort={sort}
                onSort={setSort}
              />
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedDocuments.map(doc => (
            <DocumentRow
              key={doc.id}
              document={doc}
              isSelected={doc.id === selectedId}
              onClick={() => onSelect(doc.id === selectedId ? null : doc.id)}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}
