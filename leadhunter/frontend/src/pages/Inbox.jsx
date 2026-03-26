import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchInbox, markReplyRead } from '../api/client'

export default function Inbox() {
  const qc = useQueryClient()
  const { data: replies, isLoading } = useQuery({
    queryKey: ['inbox'],
    queryFn: () => fetchInbox(1),
    refetchInterval: 60_000,
  })

  const readMutation = useMutation({
    mutationFn: (id) => markReplyRead(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['inbox'] })
      qc.invalidateQueries({ queryKey: ['inbox-unread'] })
    },
  })

  if (isLoading) return <div className="p-8 text-slate-600">Loading…</div>

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Inbox</h1>
        <p className="text-slate-600 text-sm mt-1">Inbound replies matched to leads (via Gmail sync)</p>
      </div>

      <ul className="space-y-3">
        {(replies || []).map((r) => (
          <li
            key={r.id}
            className={`rounded-lg border p-4 ${
              r.is_read ? 'border-slate-200 bg-white' : 'border-teal-300 bg-teal-50/40'
            }`}
          >
            <div className="flex justify-between gap-2">
              <div>
                <p className="font-medium text-slate-900">{r.subject || '(no subject)'}</p>
                <p className="text-xs text-slate-500 mt-1">{r.from_email}</p>
                <p className="text-sm text-slate-700 mt-2">{r.body_snippet}</p>
              </div>
              {!r.is_read && (
                <button
                  type="button"
                  className="text-xs text-teal-700 shrink-0"
                  onClick={() => readMutation.mutate(r.id)}
                >
                  Mark read
                </button>
              )}
            </div>
          </li>
        ))}
        {(!replies || replies.length === 0) && (
          <li className="text-center text-slate-500 py-12 border border-dashed border-slate-200 rounded-lg">
            No inbound messages yet
          </li>
        )}
      </ul>
    </div>
  )
}
