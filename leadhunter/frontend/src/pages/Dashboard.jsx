import { useQuery } from '@tanstack/react-query'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { fetchStats, fetchScraperHistory } from '../api/client'
import DashboardStats from '../components/DashboardStats'

const COLORS = ['#0d9488', '#64748b', '#f59e0b', '#ef4444', '#6366f1', '#8b5cf6']

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({ queryKey: ['stats'], queryFn: fetchStats })
  const { data: history } = useQuery({ queryKey: ['scraper-history'], queryFn: fetchScraperHistory })

  if (isLoading) {
    return <div className="p-8 text-slate-600">Loading…</div>
  }

  const statusData = stats?.leads_by_status
    ? Object.entries(stats.leads_by_status).map(([name, value]) => ({ name, value }))
    : []

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
        <p className="text-slate-600 text-sm mt-1">Pipeline overview and scrape activity</p>
      </div>

      <DashboardStats stats={stats} />

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Score distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.score_distribution || []}>
                <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#0d9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Leads by industry</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.leads_by_industry || []}
                  dataKey="count"
                  nameKey="industry"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ industry, percent }) => `${industry} ${(percent * 100).toFixed(0)}%`}
                >
                  {(stats?.leads_by_industry || []).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Geography</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={Object.entries(stats?.geography_wi_il || {}).map(([name, count]) => ({
                  name,
                  count,
                }))}
              >
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#64748b" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Pipeline by status</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusData}>
                <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={60} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#0d9488" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-100">
          <h3 className="text-sm font-semibold text-slate-800">Recent scrape runs</h3>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-600 text-xs uppercase">
            <tr>
              <th className="text-left px-4 py-2">Source</th>
              <th className="text-left px-4 py-2">Status</th>
              <th className="text-left px-4 py-2">Found</th>
              <th className="text-left px-4 py-2">New</th>
              <th className="text-left px-4 py-2">Updated</th>
            </tr>
          </thead>
          <tbody>
            {(history || []).slice(0, 10).map((r) => (
              <tr key={r.id} className="border-t border-slate-100">
                <td className="px-4 py-2">{r.source}</td>
                <td className="px-4 py-2">{r.status}</td>
                <td className="px-4 py-2">{r.leads_found}</td>
                <td className="px-4 py-2">{r.leads_new}</td>
                <td className="px-4 py-2">{r.leads_updated}</td>
              </tr>
            ))}
            {(!history || history.length === 0) && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  No scrape runs yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
