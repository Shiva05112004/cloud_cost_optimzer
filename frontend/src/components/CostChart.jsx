import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'

// const DEMO_DATA = [
//   { month: 'Dec', cost: 420 },
//   { month: 'Jan', cost: 380 },
//   { month: 'Feb', cost: 510 },
//   { month: 'Mar', cost: 460 },
//   { month: 'Apr', cost: 390 },
//   { month: 'May', cost: 340 },
// ]

export default function CostChart({ data = [] }) {
  const chartData = Array.isArray(data) && data.length ? data : []

  return (
    <div className="card">
      <h3 style={{ fontFamily: 'Syne', fontSize: '16px', marginBottom: '24px' }}>
        Monthly Cost Trend
      </h3>
      {chartData.length === 0 ? (
        <div style={{ height: '220px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>
          No cost data available yet.
        </div>
      ) : (
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#00d4aa" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00d4aa" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2d45" />
          <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} />
          <Tooltip
            contentStyle={{ background: '#111827', border: '1px solid #1f2d45', borderRadius: '10px', fontSize: '13px' }}
            formatter={(v) => [`$${v}`, 'Cost']}
          />
          <Area type="monotone" dataKey="cost" stroke="#00d4aa" strokeWidth={2} fill="url(#colorCost)" />
        </AreaChart>
      </ResponsiveContainer>
      )}
    </div>
  )
}