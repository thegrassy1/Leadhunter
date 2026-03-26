export default function LeadDetail({ lead, onClose }) {
  if (!lead) return null
  const bd = lead.score_breakdown || {}

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md bg-white border-l border-slate-200 shadow-xl z-50 flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-slate-100">
        <h2 className="text-lg font-semibold text-slate-900 truncate pr-2">
          {lead.business_name || 'Lead'}
        </h2>
        <button
          type="button"
          onClick={onClose}
          className="text-slate-500 hover:text-slate-800 text-sm"
        >
          Close
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase">Score</p>
          <p className="text-2xl font-bold text-teal-700">{lead.lead_score}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase mb-1">Breakdown</p>
          <ul className="space-y-1 text-slate-700">
            {Object.entries(bd).map(([k, v]) => (
              <li key={k} className="flex justify-between">
                <span>{k}</span>
                <span className="font-medium">{v}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <p className="text-xs text-slate-500">Location</p>
            <p>
              {lead.city}, {lead.state} {lead.postal_code || ''}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Industry</p>
            <p>{lead.industry || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Asking</p>
            <p>{lead.asking_price != null ? `$${lead.asking_price.toLocaleString()}` : '—'}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Revenue</p>
            <p>{lead.annual_revenue != null ? `$${lead.annual_revenue.toLocaleString()}` : '—'}</p>
          </div>
        </div>
        {lead.description && (
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase mb-1">Description</p>
            <p className="text-slate-700 whitespace-pre-wrap max-h-48 overflow-y-auto">{lead.description}</p>
          </div>
        )}
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase mb-1">Contact</p>
          <p>{lead.owner_email || '—'}</p>
          <p>{lead.owner_phone || ''}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase mb-1">Listing</p>
          {lead.source_url && (
            <a
              href={lead.source_url}
              target="_blank"
              rel="noreferrer"
              className="text-teal-700 hover:underline break-all"
            >
              {lead.source_url}
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
