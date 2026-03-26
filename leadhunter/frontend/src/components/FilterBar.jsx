export default function FilterBar({ filters, onChange }) {
  return (
    <div className="flex flex-wrap gap-3 items-end bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-600">
        Search
        <input
          className="border border-slate-300 rounded px-2 py-1.5 text-sm min-w-[180px]"
          value={filters.q || ''}
          onChange={(e) => onChange({ ...filters, q: e.target.value || undefined })}
          placeholder="Name, city, description"
        />
      </label>
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-600">
        State
        <select
          className="border border-slate-300 rounded px-2 py-1.5 text-sm"
          value={filters.state || ''}
          onChange={(e) => onChange({ ...filters, state: e.target.value || undefined })}
        >
          <option value="">All</option>
          <option value="WI">WI</option>
          <option value="IL">IL</option>
        </select>
      </label>
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-600">
        Status
        <select
          className="border border-slate-300 rounded px-2 py-1.5 text-sm"
          value={filters.status || ''}
          onChange={(e) => onChange({ ...filters, status: e.target.value || undefined })}
        >
          <option value="">All</option>
          {['new', 'researching', 'contacted', 'follow_up', 'interested', 'replied', 'not_interested', 'disqualified'].map(
            (s) => (
              <option key={s} value={s}>
                {s}
              </option>
            )
          )}
        </select>
      </label>
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-600">
        Min score
        <input
          type="number"
          min={0}
          max={100}
          className="border border-slate-300 rounded px-2 py-1.5 text-sm w-20"
          value={filters.min_score ?? ''}
          onChange={(e) =>
            onChange({
              ...filters,
              min_score: e.target.value ? Number(e.target.value) : undefined,
            })
          }
        />
      </label>
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-600">
        Source
        <select
          className="border border-slate-300 rounded px-2 py-1.5 text-sm"
          value={filters.source || ''}
          onChange={(e) => onChange({ ...filters, source: e.target.value || undefined })}
        >
          <option value="">All</option>
          <option value="bizbuysell">BizBuySell</option>
          <option value="bizquest">BizQuest</option>
          <option value="businessbroker">BusinessBroker</option>
        </select>
      </label>
    </div>
  )
}
