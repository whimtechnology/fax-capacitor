// Document Type Configuration
// Keys must match exact snake_case values from backend
export const DOCUMENT_TYPES = {
  lab_result: { label: 'Lab Result', color: '#7C3AED' },
  referral_response: { label: 'Referral Response', color: '#2563EB' },
  prior_auth_decision: { label: 'Prior Auth Decision', color: '#DC2626' },
  pharmacy_request: { label: 'Pharmacy Request', color: '#059669' },
  insurance_correspondence: { label: 'Insurance Correspondence', color: '#6B7280' },
  records_request: { label: 'Records Request', color: '#D97706' },
  marketing_junk: { label: 'Marketing / Junk', color: '#9CA3AF' },
  other: { label: 'Needs Review', color: '#3B82F6' }
}

// Priority Configuration
export const PRIORITIES = {
  critical: { label: 'Critical', color: '#DC2626', order: 0 },
  high: { label: 'High', color: '#EA580C', order: 1 },
  medium: { label: 'Medium', color: '#CA8A04', order: 2 },
  low: { label: 'Low', color: '#16A34A', order: 3 },
  none: { label: 'None', color: '#9CA3AF', order: 4 }
}

// Status Configuration
export const STATUSES = {
  classified: { label: 'UNREVIEWED', color: '#2563EB' },
  reviewed: { label: 'REVIEWED', color: '#16A34A' },
  flagged: { label: 'FLAGGED', color: '#D97706', emoji: true },
  dismissed: { label: 'DISMISSED', color: '#9CA3AF' }
}

// Flag Configuration
// Keys must match exact values from backend flags array
export const FLAGS = {
  incomplete_document: { label: 'INCOMPLETE', textColor: '#B91C1C', bgColor: '#FEF2F2', borderColor: '#FECACA' },
  possibly_misdirected: { label: 'MISDIRECTED', textColor: '#7C3AED', bgColor: '#F5F3FF', borderColor: '#DDD6FE' },
  multi_document_bundle: { label: 'BUNDLE', textColor: '#B45309', bgColor: '#FFFBEB', borderColor: '#FDE68A' }
}

// Stat Card Configuration
export const STAT_CARDS = [
  { key: 'total', label: 'Total Faxes', color: '#111827', clickable: true },
  { key: 'unreviewed', label: 'Unreviewed', color: '#EA580C', clickable: true },
  { key: 'urgent', label: 'Urgent', color: '#DC2626', clickable: true },
  { key: 'reviewed', label: 'Reviewed', color: '#16A34A', clickable: true },
  { key: 'flagged', label: 'Flagged', color: '#D97706', clickable: true },
  { key: 'confidence', label: 'Avg Confidence', color: '#2563EB', clickable: false }
]

// Filter Options
export const TYPE_FILTER_OPTIONS = [
  { value: '', label: 'All Types' },
  { value: 'lab_result', label: 'Lab Result' },
  { value: 'referral_response', label: 'Referral Response' },
  { value: 'prior_auth_decision', label: 'Prior Auth Decision' },
  { value: 'pharmacy_request', label: 'Pharmacy Request' },
  { value: 'insurance_correspondence', label: 'Insurance Correspondence' },
  { value: 'records_request', label: 'Records Request' },
  { value: 'marketing_junk', label: 'Marketing / Junk' },
  { value: 'other', label: 'Needs Review' }
]

export const STATUS_FILTER_OPTIONS = [
  { value: 'unreviewed', label: 'Unreviewed' },
  { value: '', label: 'All Statuses' },
  { value: 'urgent', label: 'Urgent Only' },
  { value: 'new', label: 'New (No Action)' },
  { value: 'flagged', label: 'Flagged' },
  { value: 'reviewed', label: 'Reviewed' },
  { value: 'dismissed', label: 'Dismissed' }
]

// Confidence thresholds (per design spec)
export const CONFIDENCE_THRESHOLDS = {
  high: 0.85,
  medium: 0.65
}

// Default filter state
export const DEFAULT_FILTERS = {
  type: '',
  status: 'unreviewed'
}

// Sort configuration
export const SORT_COLUMNS = [
  { key: 'priority', label: '', sortable: true, width: 'w-10' },
  { key: 'document_type', label: 'Type', sortable: true, width: 'w-auto' },
  { key: 'flags', label: 'Flags', sortable: false, width: 'w-20' },
  { key: 'patient_name', label: 'Patient', sortable: true, width: 'w-auto' },
  { key: 'sending_facility', label: 'From', sortable: true, width: 'w-auto' },
  { key: 'confidence', label: 'Conf.', sortable: true, width: 'w-auto' },
  { key: 'upload_time', label: 'Received', sortable: true, width: 'w-auto' },
  { key: 'status', label: 'Status', sortable: false, width: 'w-auto' }
]

// Default sort
export const DEFAULT_SORT = {
  key: 'priority',
  order: 'asc'
}
