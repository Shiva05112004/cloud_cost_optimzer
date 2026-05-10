export default function RecommendationCard({ rec }) {
  const riskColor = { low: 'var(--accent)', medium: 'var(--warn)', high: 'var(--danger)', none: 'var(--muted)' }
  const riskClass = { low: 'badge-green', medium: 'badge-yellow', high: 'badge-red', none: '' }

  return (
    <div className="card" style={{ borderLeft: `3px solid ${riskColor[rec.risk] || 'var(--border)'}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <div>
          <div style={{ fontFamily: 'Syne', fontSize: '14px', fontWeight: 700 }}>
            {rec.instance_id}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '2px' }}>
            {rec.issue}
          </div>
        </div>
        <span className={`badge ${riskClass[rec.risk]}`}>
          {rec.risk} risk
        </span>
      </div>

      <div style={{
        background: 'var(--bg3)', borderRadius: '8px',
        padding: '10px 14px', marginBottom: '14px',
        fontSize: '13px', color: 'var(--accent)',
      }}>
        ⟶ {rec.action}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--muted)' }}>Est. savings</div>
          <div style={{ fontSize: '20px', fontFamily: 'Syne', fontWeight: 700, color: 'var(--accent)' }}>
            ${rec.estimated_savings?.toFixed(2)}<span style={{ fontSize: '12px' }}>/mo</span>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '11px', color: 'var(--muted)' }}>Confidence</div>
          <div style={{ fontSize: '16px', fontWeight: 600 }}>
            {Math.round((rec.confidence || 0) * 100)}%
          </div>
        </div>
      </div>
    </div>
  )
}