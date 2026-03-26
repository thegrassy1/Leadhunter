export default function EmailComposer({ draft, onChange, onSend, sending }) {
  if (!draft) {
    return <p className="text-sm text-slate-500">Generate a draft to get started.</p>
  }
  return (
    <div className="space-y-3">
      <label className="block text-xs font-medium text-slate-600">
        Subject
        <input
          className="mt-1 w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
          value={draft.subject || ''}
          onChange={(e) => onChange({ ...draft, subject: e.target.value })}
        />
      </label>
      <label className="block text-xs font-medium text-slate-600">
        Body
        <textarea
          className="mt-1 w-full border border-slate-300 rounded px-2 py-2 text-sm min-h-[200px] font-sans"
          value={draft.body || ''}
          onChange={(e) => onChange({ ...draft, body: e.target.value })}
        />
      </label>
      <button
        type="button"
        onClick={onSend}
        disabled={sending}
        className="bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-md"
      >
        {sending ? 'Sending…' : 'Approve & Send'}
      </button>
    </div>
  )
}
