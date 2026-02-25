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
          <img
            src="/Fax_Capacitor_Logo.png"
            alt="Fax Capacitor Logo"
            className="w-14 h-14 object-contain"
          />
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
