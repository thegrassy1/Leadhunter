import { Routes, Route, NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Dashboard from './pages/Dashboard'
import Leads from './pages/Leads'
import Scraper from './pages/Scraper'
import Outreach from './pages/Outreach'
import Inbox from './pages/Inbox'
import { fetchUnreadCount } from './api/client'

const nav = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/leads', label: 'Leads' },
  { to: '/scraper', label: 'Scraper' },
  { to: '/outreach', label: 'Outreach' },
  { to: '/inbox', label: 'Inbox' },
]

export default function App() {
  const { data: unread } = useQuery({
    queryKey: ['inbox-unread'],
    queryFn: fetchUnreadCount,
    refetchInterval: 60_000,
  })

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="w-56 shrink-0 bg-[#1a2332] text-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-700/80">
          <h1 className="text-lg font-semibold tracking-tight text-white">LeadHunter</h1>
          <p className="text-xs text-slate-400 mt-1">Acquisition pipeline</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {nav.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-teal-700/30 text-white'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <span>{label}</span>
              {to === '/inbox' && unread?.count > 0 && (
                <span className="bg-teal-600 text-white text-xs px-2 py-0.5 rounded-full">
                  {unread.count}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leads" element={<Leads />} />
          <Route path="/scraper" element={<Scraper />} />
          <Route path="/outreach" element={<Outreach />} />
          <Route path="/inbox" element={<Inbox />} />
        </Routes>
      </main>
    </div>
  )
}
