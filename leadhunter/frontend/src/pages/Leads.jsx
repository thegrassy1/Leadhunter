import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchLeads, patchLead } from '../api/client'
import FilterBar from '../components/FilterBar'
import LeadTable from '../components/LeadTable'
import LeadDetail from '../components/LeadDetail'

export default function Leads() {
  const [filters, setFilters] = useState({})
  const [page, setPage] = useState(1)
  const [selected, setSelected] = useState(null)
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['leads', filters, page],
    queryFn: () => fetchLeads({ ...filters, page, page_size: 25 }),
  })

  const mutation = useMutation({
    mutationFn: ({ id, status }) => patchLead(id, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })

  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Leads</h1>
        <p className="text-slate-600 text-sm mt-1">Filter, sort, and manage acquisition targets</p>
      </div>

      <FilterBar filters={filters} onChange={(f) => { setFilters(f); setPage(1) }} />

      {isLoading ? (
        <p className="text-slate-600">Loading…</p>
      ) : (
        <>
          <LeadTable
            leads={data?.items || []}
            onSelect={setSelected}
            onStatusChange={(id, status) => mutation.mutate({ id, status })}
          />
          <div className="flex justify-between items-center text-sm text-slate-600">
            <span>
              Page {page} · {data?.total ?? 0} total
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={page <= 1}
                className="px-3 py-1 rounded border border-slate-300 disabled:opacity-40"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                Prev
              </button>
              <button
                type="button"
                disabled={!data || page * (data.page_size || 25) >= (data.total || 0)}
                className="px-3 py-1 rounded border border-slate-300 disabled:opacity-40"
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      {selected && (
        <>
          <div
            className="fixed inset-0 bg-black/20 z-40"
            aria-hidden
            onClick={() => setSelected(null)}
          />
          <LeadDetail lead={selected} onClose={() => setSelected(null)} />
        </>
      )}
    </div>
  )
}
