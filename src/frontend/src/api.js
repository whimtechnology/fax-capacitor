const API_BASE = '/api'

/**
 * Fetch wrapper with error handling
 */
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  } catch (err) {
    if (err.message === 'Failed to fetch') {
      throw new Error('Cannot connect to server. Is the backend running?')
    }
    throw err
  }
}

/**
 * Get summary statistics
 */
export async function getStats() {
  return fetchApi('/stats/summary')
}

/**
 * Get documents with optional filters
 * @param {Object} params - Query parameters
 * @param {string} params.status - Filter by status
 * @param {string} params.document_type - Filter by type
 * @param {string} params.priority - Filter by priority (comma-separated)
 * @param {string} params.sort_by - Sort field
 * @param {string} params.sort_order - Sort direction (asc/desc)
 * @param {number} params.limit - Max results
 * @param {number} params.offset - Offset for pagination
 */
export async function getDocuments(params = {}) {
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value)
    }
  })

  const queryString = queryParams.toString()
  const endpoint = queryString ? `/documents?${queryString}` : '/documents'

  return fetchApi(endpoint)
}

/**
 * Get a single document by ID
 */
export async function getDocument(id) {
  return fetchApi(`/documents/${id}`)
}

/**
 * Update a document
 * @param {number} id - Document ID
 * @param {Object} data - Update data
 * @param {string} data.status - New status
 * @param {string} data.document_type - New type
 * @param {string} data.notes - Notes
 * @param {string} data.reviewed_by - Reviewer name
 */
export async function updateDocument(id, data) {
  return fetchApi(`/documents/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  })
}

/**
 * Upload PDF files
 * @param {FileList|File[]} files - PDF files to upload
 * @param {function} onProgress - Progress callback (optional)
 */
export async function uploadDocuments(files, onProgress) {
  const formData = new FormData()

  Array.from(files).forEach(file => {
    formData.append('files', file)
  })

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

/**
 * Get PDF URL for a document
 */
export function getPdfUrl(documentId) {
  return `${API_BASE}/documents/${documentId}/pdf`
}

/**
 * Health check
 */
export async function healthCheck() {
  return fetchApi('/health')
}
