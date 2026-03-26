import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchLeads, createDraft, patchDraft, sendDraft } from '../api/client'
import EmailComposer from '../components/EmailComposer'

export default function Outreach() {
  const qc = useQueryClient()
  const [selectedId, setSelectedId] = useState(null)
  const [draft, setDraft] = useState(null)

  const { data: contacted } = useQuery({
    queryKey: ['leads', 'contacted'],
    queryFn: () => fetchLeads({ status: 'contacted', page_size: 100 }),
  })
  const { data: follow } = useQuery({
    queryKey: ['leads', 'follow'],
    queryFn: () => fetchLeads({ status: 'follow_up', page_size: 100 }),
  })

  const items = [...(contacted?.items || []), ...(follow?.items || [])]
  const unique = items.filter((l, i, a) => a.findIndex((x) => x.id === l.id) === i)

  const genMutation = useMutation({
    mutationFn: (leadId) => createDraft(leadId),
    onSuccess: (d) => {
      setDraft(d)
      qc.invalidateQueries({ queryKey: ['drafts'] })
    },
  })

  const sendMutation = useMutation({
    mutationFn: async () => {
      if (!draft?.id) throw new Error('No draft')
      await patchDraft(draft.id, { subject: draft.subject, body: draft.body })
      return sendDraft(draft.id)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['leads'] })
      setDraft(null)
    },
  })

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Outreach</h1>
        <p className="text-slate-600 text-sm mt-1">
          Draft with Claude, review, send via Gmail when credentials are configured
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
          <div className="px-4 py-3 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-800">Contacted / follow-up</h2>
          </div>
          <ul className="divide-y divide-slate-100 max-h-[420px] overflow-y-auto">
            {unique.map((l) => (
              <li key={l.id}>
                <button
                  type="button"
                  className={`w-full text-left px-4 py-3 text-sm hover:bg-slate-50 ${
                    selectedId === l.id ? 'bg-teal-50' : ''
                  }`}
                  onClick={() => setSelectedId(l.id)}
                >
                  <span className="font-medium text-slate-900">{l.business_name || '—'}</span>
                  <span className="block text-xs text-slate-500">
                    {l.city}, {l.state} · {l.owner_email || 'no email'}
                  </span>
                </button>
              </li>
            ))}
            {unique.length === 0 && (
              <li className="px-4 py-8 text-center text-slate-500 text-sm">No leads in this stage</li>
            )}
          </ul>
          <div className="p-4 border-t border-slate-100">
            <button
              type="button"
              disabled={!selectedId || genMutation.isPending}
              onClick={() => genMutation.mutate(selectedId)}
              className="w-full py-2 rounded-md bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-sm font-medium"
            >
              {genMutation.isPending ? 'Generating…' : 'Generate email draft'}
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">Composer</h2>
          <EmailComposer
            draft={draft}
            onChange={(d) => setDraft(d)}
            onSend={() => sendMutation.mutate()}
            sending={sendMutation.isPending}
          />
          {genMutation.isError && (
            <p className="text-red-600 text-xs mt-2">Could not generate draft (check API key / email).</p>
          )}
        </div>
      </div>
    </div>
  )
}
