import { useEffect } from 'react'
import { getRecommendations } from '../api/recommendations.api'
import useDashboardStore from '../store/useDashboardStore'
import RecommendationCard from '../components/RecommendationCard'
import LoadingSpinner from '../components/LoadingSpinner'

export default function RecommendationsPage() {
  const { recommendations, totalSavings, loading, setRecommendations, setLoading } = useDashboardStore()

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const res = await getRecommendations()
        setRecommendations(res.data.recommendations || [], res.data.total_potential_savings || 0)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div>
      <h1 className="page-title">Recommendations</h1>
      <p className="page-sub">
        {recommendations.length > 0
          ? `${recommendations.length} issues found — estimated savings $${totalSavings.toFixed(2)}/month`
          : 'No recommendations yet'
        }
      </p>

      {loading
        ? <LoadingSpinner text="Analysing your cloud..." />
        : recommendations.length === 0
        ? (
          <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
            <div style={{ fontSize: '40px', marginBottom: '16px' }}>✦</div>
            <p style={{ color: 'var(--muted)' }}>No issues detected. Your cloud looks healthy!</p>
          </div>
        )
        : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            {recommendations.map((rec, i) => (
              <RecommendationCard key={i} rec={rec} />
            ))}
          </div>
        )
      }
    </div>
  )
}