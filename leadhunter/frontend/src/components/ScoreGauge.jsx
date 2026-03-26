export default function ScoreGauge({ score }) {
  const n = Number(score) || 0
  let color = 'bg-red-500'
  if (n >= 70) color = 'bg-emerald-500'
  else if (n >= 40) color = 'bg-amber-500'

  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-16 rounded-full bg-slate-200 overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${Math.min(100, n)}%` }} />
      </div>
      <span className="text-sm font-semibold tabular-nums text-slate-800">{n}</span>
    </div>
  )
}
