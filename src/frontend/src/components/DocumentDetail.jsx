import { useState } from 'react'
import { DOCUMENT_TYPES, PRIORITIES, CONFIDENCE_THRESHOLDS } from '../constants'
import FlagBadge from './FlagBadge'
import ActionButtons from './ActionButtons'
import PdfViewer from './PdfViewer'
import { updateDocument } from '../api'

function TypeBadge({ type }) {
  const config = DOCUMENT_TYPES[type] || DOCUMENT_TYPES.unclassified

  return (
    <span
      className="inline-flex items-center px-2.5 py-1 rounded text-sm font-medium"
      style={{
        color: config.color,
        backgroundColor: `${config.color}11`
      }}
    >
      {config.label}
    </span>
  )
}

function formatSmartDate(dateStr) {
  if (!dateStr) return '—'

  const date = new Date(dateStr)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const timeStr = date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })

  if (dateOnly.getTime() === today.getTime()) {
    return `Today, ${timeStr}`
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

function formatDocumentDate(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function InfoRow({ label, value, mono = false }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-gray-100 last:border-0">
      <span className="text-sm text-gray-500">{label}</span>
      <span className={`text-sm text-gray-900 ${mono ? 'font-mono' : ''}`}>
        {value || '—'}
      </span>
    </div>
  )
}

export default function DocumentDetail({ document, onClose, onAction }) {
  const [isLoading, setIsLoading] = useState(false)

  if (!document) {
    return null
  }

  const {
    id,
    document_type,
    flags,
    priority,
    confidence,
    page_count,
    extracted_fields,
    upload_time,
    processing_time_ms,
    filename
  } = document

  const patientName = extracted_fields?.patient_name || 'Unknown Patient'
  const patientDob = extracted_fields?.patient_dob
  const facility = extracted_fields?.sending_facility
  const provider = extracted_fields?.sending_provider
  const phoneNumber = extracted_fields?.phone_number
  const faxNumber = extracted_fields?.fax_origin_number
  const keyDetails = extracted_fields?.key_details
  const documentDate = extracted_fields?.document_date
  const urgencyIndicators = extracted_fields?.urgency_indicators || []

  const priorityConfig = PRIORITIES[priority] || PRIORITIES.none

  let confidenceColor
  if (confidence >= CONFIDENCE_THRESHOLDS.high) {
    confidenceColor = '#16A34A'
  } else if (confidence >= CONFIDENCE_THRESHOLDS.medium) {
    confidenceColor = '#CA8A04'
  } else {
    confidenceColor = '#DC2626'
  }

  const handleAction = async (action) => {
    setIsLoading(true)
    try {
      let data = {}
      switch (action) {
        case 'review':
          data = { status: 'reviewed', reviewed_by: 'Staff' }
          break
        case 'flag':
          data = { status: 'flagged' }
          break
        case 'dismiss':
          data = { status: 'dismissed' }
          break
      }

      await updateDocument(id, data)
      onAction?.()
      onClose()
    } catch (err) {
      console.error('Action failed:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-[420px] bg-white border-l border-gray-200 shadow-lg sticky top-0 h-screen overflow-y-auto detail-panel">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-start justify-between mb-3">
          <div className="flex flex-wrap items-center gap-2">
            <TypeBadge type={document_type} />
            {flags?.map((flag, idx) => (
              <FlagBadge key={idx} flag={flag} />
            ))}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        <h2 className="text-xl font-bold text-gray-900">{patientName}</h2>
        {patientDob && (
          <p className="text-sm text-gray-500 mt-1">
            DOB: {formatDocumentDate(patientDob)}
          </p>
        )}
      </div>

      {/* Priority / Confidence / Pages */}
      <div className="px-4 py-3 border-b border-gray-200 flex justify-between">
        <div className="text-center">
          <div
            className="text-sm font-semibold"
            style={{ color: priorityConfig.color }}
          >
            {priorityConfig.label}
          </div>
          <div className="text-xs text-gray-400">Priority</div>
        </div>
        <div className="text-center">
          <div
            className="text-sm font-semibold font-mono"
            style={{ color: confidenceColor }}
          >
            {Math.round(confidence * 100)}%
          </div>
          <div className="text-xs text-gray-400">Confidence</div>
        </div>
        <div className="text-center">
          <div className="text-sm font-semibold text-gray-700 font-mono">
            {page_count}
          </div>
          <div className="text-xs text-gray-400">{page_count === 1 ? 'Page' : 'Pages'}</div>
        </div>
      </div>

      {/* Sender Info */}
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Sender</h3>
        {facility && (
          <p className="text-sm font-semibold text-gray-900">{facility}</p>
        )}
        {provider && (
          <p className="text-sm text-gray-600">{provider}</p>
        )}
        <div className="mt-2 flex flex-wrap gap-3">
          {phoneNumber && (
            <span className="text-sm text-blue-600 flex items-center gap-1">
              <span>&#128222;</span>
              <span className="font-mono">{phoneNumber}</span>
            </span>
          )}
          {faxNumber && (
            <span className="text-sm text-gray-500 flex items-center gap-1">
              <span>&#128224;</span>
              <span className="font-mono">{faxNumber}</span>
            </span>
          )}
        </div>
      </div>

      {/* Summary */}
      {keyDetails && (
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Summary</h3>
          <div className="bg-gray-50 rounded p-3 text-sm text-gray-700">
            {keyDetails}
          </div>
        </div>
      )}

      {/* Urgency Indicators */}
      {urgencyIndicators.length > 0 && (
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Urgency Indicators</h3>
          <div className="flex flex-wrap gap-2">
            {urgencyIndicators.map((indicator, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-2 py-1 rounded text-xs font-bold uppercase"
                style={{
                  color: '#DC2626',
                  backgroundColor: '#FEF2F2',
                  border: '1px solid #FECACA'
                }}
              >
                {indicator}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Document Info */}
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Document Info</h3>
        <div>
          <InfoRow label="Document Date" value={formatDocumentDate(documentDate)} />
          <InfoRow label="Received" value={formatSmartDate(upload_time)} mono />
          <InfoRow
            label="Processing"
            value={processing_time_ms ? `${(processing_time_ms / 1000).toFixed(1)}s` : '—'}
            mono
          />
          <InfoRow label="Filename" value={filename} mono />
        </div>
      </div>

      {/* PDF Preview */}
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Preview</h3>
        <PdfViewer documentId={id} />
      </div>

      {/* Action Buttons */}
      <div className="px-4 py-4">
        <ActionButtons
          onReview={() => handleAction('review')}
          onFlag={() => handleAction('flag')}
          onDismiss={() => handleAction('dismiss')}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}
