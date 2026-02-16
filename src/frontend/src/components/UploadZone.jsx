import { useState, useRef } from 'react'
import { uploadDocuments } from '../api'

export default function UploadZone({ onUploadComplete }) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'application/pdf'
    )

    if (files.length > 0) {
      await handleUpload(files)
    }
  }

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files)
    if (files.length > 0) {
      await handleUpload(files)
    }
    // Reset input so same file can be selected again
    e.target.value = ''
  }

  const handleUpload = async (files) => {
    setIsUploading(true)
    setUploadStatus({ type: 'uploading', message: `Processing ${files.length} file(s)...` })

    try {
      const result = await uploadDocuments(files)

      // Build message based on success/failure counts
      let message
      if (result.failed === 0) {
        message = `${result.uploaded} document(s) classified successfully`
      } else if (result.uploaded === 0) {
        message = `${result.failed} document(s) failed to process`
      } else {
        message = `${result.uploaded} classified, ${result.failed} failed`
      }

      setUploadStatus({
        type: result.uploaded > 0 ? 'success' : 'error',
        message
      })
      onUploadComplete?.()

      // Clear success message after 3 seconds
      setTimeout(() => setUploadStatus(null), 3000)
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err.message || 'Upload failed'
      })
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="px-6 py-3">
      <div
        className={`upload-zone rounded-lg p-4 ${isDragging ? 'drag-active' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <div className="flex items-center justify-center gap-4">
          <svg
            className={`w-8 h-8 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Drag and drop PDF files here, or{' '}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-blue-600 hover:underline font-medium"
                disabled={isUploading}
              >
                browse
              </button>
            </p>
            <p className="text-xs text-gray-400 mt-1">PDF files only</p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {uploadStatus && (
          <div
            className={`mt-3 text-sm text-center py-2 rounded ${
              uploadStatus.type === 'uploading'
                ? 'bg-blue-50 text-blue-600'
                : uploadStatus.type === 'success'
                ? 'bg-green-50 text-green-600'
                : 'bg-red-50 text-red-600'
            }`}
          >
            {uploadStatus.type === 'uploading' && (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
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
                {uploadStatus.message}
              </span>
            )}
            {uploadStatus.type !== 'uploading' && uploadStatus.message}
          </div>
        )}
      </div>
    </div>
  )
}
