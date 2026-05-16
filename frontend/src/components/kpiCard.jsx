export default function KpiCard({ title, value, sub, color = 'var(--accent)', icon }) {
  return (
    <div className="card" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Glow blob */}
      <div style={{
        position: 'absolute', top: '-20px', right: '-20px',
        width: '80px', height: '80px', borderRadius: '50%',
        background: color, opacity: 0.08, filter: 'blur(20px)',
      }} />
      <div style={{ fontSize: '24px', marginBottom: '12px' }}>{icon}</div>
      <div style={{ fontSize: '12px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>
        {title}
      </div>
      <div style={{ fontSize: '28px', fontFamily: 'Syne', fontWeight: 700, color }}>
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '4px' }}>{sub}</div>
      )}
    </div>
  )
}