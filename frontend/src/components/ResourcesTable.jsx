export default function ResourceTable({ instances = [] }) {
  const cpuColor = (cpu) => {
    if (cpu < 10) return 'var(--danger)'
    if (cpu < 20) return 'var(--warn)'
    return 'var(--accent)'
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
              <td>
                <span className={`badge ${inst.state === 'running' ? 'badge-green' : 'badge-red'}`}>
                  {inst.state}
                </span>
              </td>
              <td style={{ color: cpuColor(inst.avg_cpu), fontWeight: 600 }}>
                {inst.avg_cpu?.toFixed(1)}%
              </td>
              <td style={{ color: 'var(--muted)' }}>{inst.region}</td>
              <td>
                {inst.avg_cpu < 10
                  ? <span className="badge badge-red">Idle</span>
                  : inst.avg_cpu < 20
                  ? <span className="badge badge-yellow">Low</span>
                  : <span className="badge badge-green">Healthy</span>
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}