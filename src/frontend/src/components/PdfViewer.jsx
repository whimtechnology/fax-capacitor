import { useState, useEffect } from 'react'
import { getPdfUrl } from '../api'

export default function PdfViewer({ documentId }) {
  const [error, setError] = useState(false)
  const [isLoaded, setIsLoaded] = useState(false)

  // Reset state when document changes
  useEffect(() => {
    setError(false)
    setIsLoaded(false)
  }, [documentId])

  if (!documentId) {
    return (
      <div className="pdf-viewer h-64 flex items-center justify-center">
        <span className="text-gray-400">No document selected</span>
      </div>
    )
  }

  // Add view parameters to encourage inline display
  const pdfUrl = `${getPdfUrl(documentId)}#toolbar=1&navpanes=0&view=FitH`

  if (error) {
    return (
      <div className="pdf-viewer h-64 flex flex-col items-center justify-center">
        <svg className="w-12 h-12 text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span className="text-gray-400 text-sm">Unable to load PDF</span>
        <a
          href={getPdfUrl(documentId)}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 text-sm text-blue-600 hover:underline"
        >
          Open in new tab
        </a>
      </div>
    )
  }

  return (
    <div className="pdf-viewer relative">
      {!isLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 h-[400px]">
          <div className="text-gray-400 text-sm">Loading PDF...</div>
        </div>
      )}
      {/* Use object tag with explicit type for inline display, iframe as fallback */}
      <object
        data={pdfUrl}
        type="application/pdf"
        className="w-full h-[400px] border-0"
        onLoad={() => setIsLoaded(true)}
        onError={() => setError(true)}
      >
        {/* Fallback iframe for browsers that don't support object for PDFs */}
        <iframe
          src={pdfUrl}
          className="w-full h-[400px] border-0"
          title="PDF Preview"
          onLoad={() => setIsLoaded(true)}
        />
      </object>
    </div>
  )
}
