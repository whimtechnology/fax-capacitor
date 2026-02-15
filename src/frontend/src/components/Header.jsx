export default function Header() {
  const today = new Date()
  const dateStr = today.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Lightning bolt icon with gradient */}
          <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-gradient-to-br from-blue-700 to-purple-600">
            <svg
              className="w-6 h-6 text-white"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Fax Capacitor</h1>
            <p className="text-sm text-gray-500">Whispering Pines Family Medicine</p>
          </div>
        </div>

        <div className="text-sm text-gray-600 font-medium">
          {dateStr}
        </div>
      </div>
    </header>
  )
}
