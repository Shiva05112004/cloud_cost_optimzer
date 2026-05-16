import { useEffect } from 'react'
import { getEC2Instances, getCosts } from '../api/resources.api'
import { getRecommendations } from '../api/recommendations.api'
import useDashboardStore from '../store/useDashboardStore'
import KpiCard from '../components/KpiCard'
import CostChart from '../components/CostChart'
import RecommendationCard from '../components/RecommendationCard'
import LoadingSpinner from '../components/LoadingSpinner'

export default function DashboardPage() {
  const {
    instances, totalCost, recommendations,
    totalSavings, loading,
    setInstances, setCosts, setRecommendations, setLoading,
  } = useDashboardStore()

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [ec2Res, costRes, recRes] = await Promise.all([
          getEC2Instances(),
          getCosts(),
          getRecommendations(),
        ])
        setInstances(ec2Res.data.instances || [])
        setCosts(costRes.data.by_service || {}, costRes.data.total_usd || 0)
        setRecommendations(
          recRes.data.recommendations || [],
          recRes.data.total_potential_savings || 0,
        )
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <LoadingSpinner text="Fetching cloud data..." />

  const idleCount = instances.filter((i) => i.avg_cpu < 10).length
  const topRecs   = recommendations.slice(0, 4)

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>
      <p className="page-sub">Your AWS cost overview — updated live</p>

      {/* KPI Cards */}
      <div className="grid-4">
        <KpiCard icon="💰" title="Monthly Cost"    value={`$${totalCost.toFixed(2)}`}   color="var(--accent2)" />
        <KpiCard icon="✦"  title="Potential Savings" value={`$${totalSavings.toFixed(2)}`} color="var(--accent)"  sub="per month" />
        <KpiCard icon="⬡"  title="EC2 Instances"  value={instances.length}              color="var(--warn)"    sub="running" />
        <KpiCard icon="⚠"  title="Idle Instances" value={idleCount}                     color="var(--danger)"  sub="need attention" />
      </div>

      {/* Chart + Top Recommendations */}
      <div className="grid-2" style={{ marginBottom: '32px' }}>
        <CostChart />
        <div className="card">
          <h3 style={{ fontFamily: 'Syne', fontSize: '16px', marginBottom: '16px' }}>
            Top Recommendations
          </h3>
          {topRecs.length === 0
            ? <p style={{ color: 'var(--muted)', fontSize: '14px' }}>No recommendations yet. Connect your AWS account.</p>
            : <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {topRecs.map((r, i) => (
                  <div key={i} style={{
                    display: 'flex', justifyContent: 'space-between',
                    padding: '10px 14px', background: 'var(--bg3)',
                    borderRadius: '10px', fontSize: '13px',
                  }}>
                    <span style={{ color: 'var(--muted)' }}>{r.instance_id}</span>
                    <span style={{ color: 'var(--accent)', fontWeight: 600 }}>
                      Save ${r.estimated_savings?.toFixed(0)}/mo
                    </span>
                  </div>
                ))}
              </div>
          }
        </div>
      </div>
    </div>
  )
}