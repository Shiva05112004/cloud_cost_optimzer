import ChatBox from './ChatBox'

export default function RecommendationCard({ rec, isPopped = false, hideChat = false }) {
  const riskColor = { low: 'var(--accent)', medium: 'var(--warn)', high: 'var(--danger)', none: 'var(--muted)' }
  const riskClass = { low: 'badge-green', medium: 'badge-yellow', high: 'badge-red', none: '' }

  return (
    <div 
      className="card" 
      style={{ 
        borderLeft: `3px solid ${riskColor[rec.risk] || 'var(--border)'}`,
        boxShadow: isPopped ? '0 4px 20px rgba(0,212,170,0.04)' : 'none',
        background: isPopped ? 'var(--bg3)' : 'var(--card-bg)',
        transition: 'all 0.3s ease-in-out',
        width: '100%',
        boxSizing: 'border-box'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <div>
          <div style={{ fontFamily: 'Syne', fontSize: '14px', fontWeight: 700 }}>
            {rec.instance_id}
            {rec.instance_name && rec.instance_name !== 'Unnamed Instance' && (
              <span style={{ fontWeight: 500, color: 'var(--muted)', marginLeft: '6px' }}>
                ({rec.instance_name})
              </span>
            )}
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

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: isPopped ? '16px' : '0px' }}>
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

      {/* ─── 💡 CHAT DISPLAY MATRIX CONTROLLER ─── */}
      {isPopped && !hideChat && (
        <div style={{ 
          marginTop: '16px', 
          borderTop: '1px solid var(--border)', 
          paddingTop: '16px',
          animation: 'fadeIn 0.2s ease-in-out'
        }}>
          <ChatBox rec={rec} />
        </div>
      )}
    </div>
  )
}




// import ChatBox from './ChatBox'
// export default function RecommendationCard({ rec }) {
//   const riskColor = { low: 'var(--accent)', medium: 'var(--warn)', high: 'var(--danger)', none: 'var(--muted)' }
//   const riskClass = { low: 'badge-green', medium: 'badge-yellow', high: 'badge-red', none: '' }

//   return (
//     <div className="card" style={{ borderLeft: `3px solid ${riskColor[rec.risk] || 'var(--border)'}` }}>
//       <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
//         <div>
//           <div style={{ fontFamily: 'Syne', fontSize: '14px', fontWeight: 700 }}>
//             {rec.instance_id}
//               {/* 💡 Dynamically adds the name in brackets if it exists and isn't Unnamed */}
//             {rec.instance_name && rec.instance_name !== 'Unnamed Instance' && (
//               <span style={{ fontWeight: 500, color: 'var(--muted)', marginLeft: '6px' }}>
//                 ({rec.instance_name})
//               </span>
//             )}
//           </div>
//           <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '2px' }}>
//             {rec.issue}
//           </div>
//         </div>
//         <span className={`badge ${riskClass[rec.risk]}`}>
//           {rec.risk} risk
//         </span>
//       </div>

//       <div style={{
//         background: 'var(--bg3)', borderRadius: '8px',
//         padding: '10px 14px', marginBottom: '14px',
//         fontSize: '13px', color: 'var(--accent)',
//       }}>
//         ⟶ {rec.action}
//       </div>

//       <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
//         <div>
//           <div style={{ fontSize: '11px', color: 'var(--muted)' }}>Est. savings</div>
//           <div style={{ fontSize: '20px', fontFamily: 'Syne', fontWeight: 700, color: 'var(--accent)' }}>
//             ${rec.estimated_savings?.toFixed(2)}<span style={{ fontSize: '12px' }}>/mo</span>
//           </div>
//         </div>
//         <div style={{ textAlign: 'right' }}>
//           <div style={{ fontSize: '11px', color: 'var(--muted)' }}>Confidence</div>
//           <div style={{ fontSize: '16px', fontWeight: 600 }}>
//             {Math.round((rec.confidence || 0) * 100)}%
//           </div>
//         </div>
//       </div>
//       <ChatBox rec={rec} />
//     </div>
//   )
// }