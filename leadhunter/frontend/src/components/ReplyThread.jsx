export default function ReplyThread({ thread }) {
  if (!thread) return null
  const items = [
    ...(thread.outbound || []).map((o) => ({ ...o, _t: 'out' })),
    ...(thread.inbound || []).map((i) => ({ ...i, _t: 'in' })),
  ]
  items.sort((a, b) => {
    const ta = a.sent_at || a.received_at || ''
    const tb = b.sent_at || b.received_at || ''
    return ta.localeCompare(tb)
  })

  return (
    <div className="space-y-3 text-sm">
      {items.map((m, idx) => (
        <div
          key={idx}
          className={`rounded-lg p-3 border ${
            m._t === 'out' ? 'border-teal-200 bg-teal-50/50' : 'border-slate-200 bg-white'
          }`}
        >
          <p className="text-xs text-slate-500 mb-1">
            {m._t === 'out' ? 'You' : m.from || 'Them'} · {m.sent_at || m.received_at || ''}
          </p>
          <p className="font-medium text-slate-700">{m.subject}</p>
          <p className="text-slate-600 mt-1 whitespace-pre-wrap">{m.body}</p>
        </div>
      ))}
    </div>
  )
}
