export default function ResourceTable({ instances = [] }) {
  const cpuColor = (cpu) => {
    const value = Number(cpu || 0)
    if (value < 10) return 'var(--danger)'
    if (value < 20) return 'var(--warn)'
    return 'var(--accent)'
  }

  const stateBadge = (state) => {
    const normalized = (state || '').toLowerCase()
    if (normalized === 'running') return <span className="badge badge-green">Running</span>
    if (normalized === 'stopped') return <span className="badge badge-red">Stopped</span>
    return <span className="badge badge-yellow">{state || 'Unknown'}</span>
  }

  if (!instances.length) return (
    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--muted)' }}>
      No instances found. Connect your AWS account first.
    </div>
  )

  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead>
          <tr>
            <th>Instance ID</th>
            <th>Type</th>
            <th>State</th>
            <th>Avg CPU</th>
            <th>Region</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {instances.map((inst) => (
            <tr key={inst.instance_id}>
              <td style={{ fontFamily: 'monospace', fontSize: '12px', color: 'var(--accent)' }}>
                {inst.instance_id}
              </td>
              <td>{inst.instance_type}</td>
              <td>{stateBadge(inst.state)}</td>
              <td style={{ color: cpuColor(inst.avg_cpu), fontWeight: 600 }}>
                {Number(inst.avg_cpu || 0).toFixed(1)}%
              </td>
              <td style={{ color: 'var(--muted)' }}>{inst.region}</td>
              <td>
                {(inst.state || '').toLowerCase() === 'running'
                  ? <span className="badge badge-green">Running</span>
                  : (inst.state || '').toLowerCase() === 'stopped'
                  ? <span className="badge badge-red">Stopped</span>
                  : <span className="badge badge-yellow">Unknown</span>
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}