export default function DashboardStats({ stats }) {
  if (!stats) return null
  const cards = [
    { label: 'Total leads', value: stats.total_leads },
    { label: 'Avg score', value: stats.avg_score?.toFixed(1) },
    { label: 'New this week', value: stats.new_this_week },
    { label: 'Replies', value: stats.replies_received },
    { label: 'Reply rate', value: `${stats.reply_rate_pct}%` },
  ]
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {cards.map((c) => (
        <div
          key={c.label}
          className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
        >
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{c.label}</p>
          <p className="text-2xl font-semibold text-slate-900 mt-1">{c.value}</p>
        </div>
      ))}
    </div>
  )
}
