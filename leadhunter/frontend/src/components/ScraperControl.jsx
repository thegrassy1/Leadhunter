export default function ScraperControl({ onRun, running }) {
  const sources = [
    { id: 'bizbuysell', label: 'BizBuySell' },
    { id: 'bizquest', label: 'BizQuest' },
    { id: 'businessbroker', label: 'BusinessBroker.net' },
  ]
  return (
    <div className="flex flex-wrap gap-2">
      {sources.map((s) => (
        <button
          key={s.id}
          type="button"
          disabled={running}
          onClick={() => onRun(s.id)}
          className="px-4 py-2 rounded-md bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-sm font-medium"
        >
          Run {s.label}
        </button>
      ))}
    </div>
  )
}
