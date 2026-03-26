import ScoreGauge from './ScoreGauge'

export default function LeadTable({ leads, onSelect, onStatusChange }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-sm text-left">
        <thead className="bg-slate-100 text-slate-600 text-xs uppercase tracking-wide">
          <tr>
            <th className="px-3 py-2">Score</th>
            <th className="px-3 py-2">Business</th>
            <th className="px-3 py-2">Location</th>
            <th className="px-3 py-2">Industry</th>
            <th className="px-3 py-2">Revenue</th>
            <th className="px-3 py-2">Employees</th>
            <th className="px-3 py-2">Status</th>
            <th className="px-3 py-2">Source</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr
              key={lead.id}
              className="border-t border-slate-100 hover:bg-slate-50 cursor-pointer"
              onClick={() => onSelect?.(lead)}
            >
              <td className="px-3 py-2 whitespace-nowrap">
                <ScoreGauge score={lead.lead_score} />
              </td>
              <td className="px-3 py-2 font-medium text-slate-900">{lead.business_name || '—'}</td>
              <td className="px-3 py-2 text-slate-600">
                {lead.city || '—'}, {lead.state || ''}
              </td>
              <td className="px-3 py-2 text-slate-600 max-w-[140px] truncate">{lead.industry || '—'}</td>
              <td className="px-3 py-2 text-slate-600 tabular-nums">
                {lead.annual_revenue != null
                  ? `$${(lead.annual_revenue / 1e6).toFixed(2)}M`
                  : '—'}
              </td>
              <td className="px-3 py-2 text-slate-600">{lead.employee_count ?? '—'}</td>
              <td className="px-3 py-2" onClick={(e) => e.stopPropagation()}>
                <select
                  className="border border-slate-200 rounded px-1 py-0.5 text-xs"
                  value={lead.status}
                  onChange={(e) => onStatusChange?.(lead.id, e.target.value)}
                >
                  {['new', 'researching', 'contacted', 'follow_up', 'interested', 'replied', 'not_interested', 'disqualified'].map(
                    (s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    )
                  )}
                </select>
              </td>
              <td className="px-3 py-2 text-slate-500 text-xs">{lead.source}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
