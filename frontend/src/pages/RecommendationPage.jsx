import { useEffect, useState } from 'react'
import { getRecommendations } from '../api/recommendations.api'
import useDashboardStore from '../store/useDashboardStore'
import RecommendationCard from '../components/RecommendationCard'
import LoadingSpinner from '../components/LoadingSpinner'

export default function RecommendationsPage() {
  const { recommendations, totalSavings, loading, setRecommendations, setLoading } = useDashboardStore()
  const [activeRec, setActiveRec] = useState(null)
  
  // State controllers for the looping toast notification
  const [showToast, setShowToast] = useState(false)

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
  }, [setRecommendations, setLoading])

  // ─── 💡 HIGH-ADVANCED LOOPING TIMING ENGINE ───
  useEffect(() => {
    // If we are currently interacting inside a RAG chat drawer, completely freeze the loop
    if (loading || recommendations.length === 0 || activeRec) {
      setShowToast(false) // Ensure the toast is hidden when not needed
      return
    }

    let loopTimer

    const runToastCycle = () => {
      // 1. Show the alert immediately
      setShowToast(true)

      // 2. Schedule it to hide after exactly 3 seconds
      loopTimer = setTimeout(() => {
        setShowToast(false)

        // 3. Keep it hidden for exactly 2 seconds, then re-trigger the cycle recursively
        loopTimer = setTimeout(() => {
          runToastCycle()
        }, 2000) // Hidden for 2 seconds

      }, 3000) // Displayed for 3 seconds
    }

    // Initialize the loop
    runToastCycle()

    // Clean up timers on component unmount or when a card is selected
    return () => clearTimeout(loopTimer)
  }, [loading, recommendations.length, activeRec])

  // Reset hooks safely when backing away from active chats
  const handleBackToList = () => {
    setActiveRec(null)
  }

  if (loading) return <LoadingSpinner text="Analysing your cloud..." />

  return (
    <div style={{ 
      display: 'flex', 
      width: '100%', 
      position: 'relative',
      gap: '24px',
      minHeight: 'calc(100vh - 48px)',
      boxSizing: 'border-box'
    }}>
      
      {/* ─── LEFT SIDE: MAIN CARDS WORKSPACE ─── */}
      <div style={{ 
        flex: 1, 
        transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
        maxWidth: activeRec ? '45%' : '100%' 
      }}>
        <h1 className="page-title">Recommendations</h1>
        <p className="page-sub">
          {recommendations.length > 0
            ? `${recommendations.length} issues found — estimated savings $${totalSavings.toFixed(2)}/month`
            : 'No recommendations yet'
          }
        </p>

        {recommendations.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '60px', marginTop: '24px' }}>
            <div style={{ fontSize: '40px', marginBottom: '16px' }}>✦</div>
            <p style={{ color: 'var(--muted)' }}>No issues detected. Your cloud looks healthy!</p>
          </div>
        ) : (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: activeRec ? '1fr' : 'repeat(2, 1fr)', 
            gap: '16px',
            marginTop: '24px'
          }}>
            {recommendations.map((rec, i) => (
              <div 
                key={i} 
                onClick={() => !activeRec && setActiveRec(rec)}
                style={{ 
                  cursor: activeRec ? 'default' : 'pointer',
                  opacity: activeRec && activeRec.instance_id !== rec.instance_id ? 0.35 : 1,
                  transform: activeRec && activeRec.instance_id === rec.instance_id ? 'scale(0.98)' : 'none',
                  transition: 'all 0.2s ease-in-out'
                }}
              >
                <RecommendationCard rec={rec} isPopped={activeRec?.instance_id === rec.instance_id} hideChat={true} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ─── RIGHT SIDE: SLIDING RAG INTERACTION PANEL ─── */}
      <div style={{
        width: activeRec ? '55%' : '0%',
        opacity: activeRec ? 1 : 0,
        pointerEvents: activeRec ? 'auto' : 'none',
        background: 'var(--bg2)',
        borderLeft: activeRec ? '1px solid var(--border)' : 'none',
        padding: activeRec ? '24px' : '0px',
        position: 'sticky',
        top: '24px',
        height: 'calc(100vh - 48px)',
        borderRadius: '16px',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
        overflowY: 'auto',
        boxSizing: 'border-box'
      }}>
        {activeRec && (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ marginBottom: '20px' }}>
              <button 
                onClick={handleBackToList}
                className="btn btn-outline"
                style={{ padding: '6px 14px', fontSize: '13px', cursor: 'pointer' }}
              >
                ← Back to List
              </button>
            </div>

            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: 'Syne', fontSize: '18px', fontWeight: 800, color: 'var(--accent)', marginBottom: '4px' }}>
                Active CloudOpt Core RAG Analysis
              </div>
              <p style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '20px' }}>
                Querying llama3.2 locally with live resource context variables.
              </p>
              <RecommendationCard rec={activeRec} isPopped={true} hideChat={false} />
            </div>
          </div>
        )}
      </div>

      {/* ─── 💡 THE INFINITE LOOP TOAST COMPONENT ─── */}
      <div style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        background: 'var(--bg2)',
        border: '1px solid var(--accent)',
        borderRadius: '12px',
        padding: '14px 20px',
        boxShadow: '0 8px 30px rgba(0, 212, 170, 0.12)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        zIndex: 1000,
        // Slide up and bounce on reveal, slide completely down when hidden
        transform: showToast ? 'translateY(0) scale(1)' : 'translateY(120px) scale(0.9)',
        opacity: showToast ? 1 : 0,
        transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
      }}>
        <div style={{
          background: 'rgba(0, 212, 170, 0.1)',
          borderRadius: '50%',
          width: '28px',
          height: '28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '14px',
          color: 'var(--accent)'
        }}>
          ✦
        </div>
        <div>
          <div style={{ fontFamily: 'Syne', fontSize: '13px', fontWeight: 700, color: 'var(--accent)' }}>
            Interactive Chat Available
          </div>
          <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px' }}>
            Click any recommendation card to launch local RAG analysis.
          </div>
        </div>
      </div>

    </div>
  )
}




// import { useEffect } from 'react'
// import { getRecommendations } from '../api/recommendations.api'
// import useDashboardStore from '../store/useDashboardStore'
// import RecommendationCard from '../components/RecommendationCard'
// import LoadingSpinner from '../components/LoadingSpinner'

// export default function RecommendationsPage() {
//   const { recommendations, totalSavings, loading, setRecommendations, setLoading } = useDashboardStore()

//   useEffect(() => {
//     const load = async () => {
//       setLoading(true)
//       try {
//         const res = await getRecommendations()
//         setRecommendations(res.data.recommendations || [], res.data.total_potential_savings || 0)
//       } catch (err) {
//         console.error(err)
//       } finally {
//         setLoading(false)
//       }
//     }
//     load()
//   }, [])

//   return (
//     <div>
//       <h1 className="page-title">Recommendations</h1>
//       <p className="page-sub">
//         {recommendations.length > 0
//           ? `${recommendations.length} issues found — estimated savings $${totalSavings.toFixed(2)}/month`
//           : 'No recommendations yet'
//         }
//       </p>

//       {loading
//         ? <LoadingSpinner text="Analysing your cloud..." />
//         : recommendations.length === 0
//         ? (
//           <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
//             <div style={{ fontSize: '40px', marginBottom: '16px' }}>✦</div>
//             <p style={{ color: 'var(--muted)' }}>No issues detected. Your cloud looks healthy!</p>
//           </div>
//         )
//         : (
//           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
//             {recommendations.map((rec, i) => (
//               <RecommendationCard key={i} rec={rec} />
//             ))}
//           </div>
//         )
//       }
//     </div>
//   )
// }