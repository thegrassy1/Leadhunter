import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchScraperHistory, fetchScraperStatus, runScraper } from '../api/client'
import ScraperControl from '../components/ScraperControl'

export default function Scraper() {
  const qc = useQueryClient()
  const { data: history, refetch: refetchHistory } = useQuery({
    queryKey: ['scraper-history'],
    queryFn: fetchScraperHistory,
    refetchInterval: 5000,
  })
  const { data: status } = useQuery({
    queryKey: ['scraper-status'],
    queryFn: fetchScraperStatus,
    refetchInterval: 5000,
  })

  const running = status?.running

  async function handleRun(source) {
    await runScraper(source)
    qc.invalidateQueries({ queryKey: ['scraper-status'] })
    refetchHistory()
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Scraper</h1>
        <p className="text-slate-600 text-sm mt-1">
          Trigger listing scrapes (respects robots.txt and rate limits on the server)
        </p>
      </div>

      {running && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          A scrape may be running — status refreshes every 5s.
        </div>
      )}

      <ScraperControl onRun={handleRun} running={running} />

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-800">Run history</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-600 text-xs uppercase">
            <tr>
              <th className="text-left px-4 py-2">Source</th>
              <th className="text-left px-4 py-2">Status</th>
              <th className="text-left px-4 py-2">Found</th>
              <th className="text-left px-4 py-2">New</th>
              <th className="text-left px-4 py-2">Updated</th>
              <th className="text-left px-4 py-2">Error</th>
            </tr>
          </thead>
          <tbody>
            {(history || []).map((r) => (
              <tr key={r.id} className="border-t border-slate-100">
                <td className="px-4 py-2">{r.source}</td>
                <td className="px-4 py-2">{r.status}</td>
                <td className="px-4 py-2">{r.leads_found}</td>
                <td className="px-4 py-2">{r.leads_new}</td>
                <td className="px-4 py-2">{r.leads_updated}</td>
                <td className="px-4 py-2 text-red-600 text-xs max-w-[200px] truncate">
                  {r.error_message || '—'}
                </td>
              </tr>
            ))}
            {(!history || history.length === 0) && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                  No runs yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
