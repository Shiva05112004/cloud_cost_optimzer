import { useEffect, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import useAuthStore from '../store/useAuthStore'

const links = [
  { to: '/dashboard',        icon: '▦', label: 'Dashboard' },
  { to: '/resources',        icon: '⬡', label: 'Resources' },
  { to: '/recommendations',  icon: '◈', label: 'Recommendations' },
  { to: '/connect',          icon: '⊕', label: 'Connect Account' },
]

export default function Sidebar() {
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()
  const [isConnected, setIsConnected] = useState(false)
  const [roleArn, setRoleArn] = useState('')

  // 💡 Hook to listen to local cloud configurations reactively
  useEffect(() => {
    const checkConnection = () => {
      try {
        const storedArn = localStorage.getItem('connected_role_arn')
        if (storedArn) {
          setIsConnected(true)
          // Trims the long ARN string into just the final descriptive role name
          const roleName = storedArn.split('/').pop() || 'AWS Role'
          setRoleArn(roleName)
        } else {
          setIsConnected(false)
          setRoleArn('')
        }
      } catch (error) {
        setIsConnected(false)
        setRoleArn('')
        console.error('Failed to retrieve role ARN from localStorage', error)
      }
    }

    checkConnection()

    // Event listeners to handle real-time UI re-renders on configuration changes
    window.addEventListener('storage', checkConnection)
    const interval = setInterval(checkConnection, 2000) // Polling fallback for local tab changes

    return () => {
      window.removeEventListener('storage', checkConnection)
      clearInterval(interval)
    }
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside style={{
      position: 'fixed', top: 0, left: 0,
      width: '240px', height: '100vh',
      background: 'var(--bg2)',
      borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column',
      padding: '24px 16px', zIndex: 100,
      boxSizing: 'border-box'
    }}>
      {/* Logo */}
      <div style={{ marginBottom: '40px', paddingLeft: '8px' }}>
        <div style={{
          fontFamily: 'Syne', fontSize: '18px',
          fontWeight: 800, color: 'var(--accent)',
          letterSpacing: '-0.5px',
        }}>
          ◉ CloudOpt
        </div>
        <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px' }}>
          Cost Optimizer
        </div>
      </div>

      {/* Nav links */}
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: '12px',
              padding: '10px 12px', borderRadius: '10px',
              fontSize: '14px', fontWeight: 500,
              textDecoration: 'none',
              color: isActive ? 'var(--accent)' : 'var(--muted)',
              background: isActive ? 'rgba(0,212,170,0.08)' : 'transparent',
              transition: 'all 0.2s',
            })}
          >
            <span style={{ fontSize: '16px' }}>{l.icon}</span>
            {l.label}
          </NavLink>
        ))}
      </nav>

      {/* ─── 💡 NEW SIDEBAR CONNECTION INDICATOR PANEL ─── */}
      <div style={{
        background: 'var(--bg3)', 
        borderRadius: '10px',
        padding: '12px 14px', 
        marginBottom: '16px',
        border: `1px solid ${isConnected ? 'rgba(16, 185, 129, 0.2)' : 'var(--border)'}`
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Status Pulse Dot */}
          <span style={{
            height: '8px', width: '8px',
            backgroundColor: isConnected ? '#10b981' : '#ef4444',
            borderRadius: '50%', display: 'inline-block',
            boxShadow: isConnected ? '0 0 6px #10b981' : '0 0 6px #ef4444'
          }} />
          <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.5px', color: isConnected ? 'var(--accent)' : 'var(--muted)' }}>
            {isConnected ? 'CONNECTED' : 'NOT CONNECTED'}
          </span>
        </div>
        
        {isConnected && (
          <div style={{ 
            fontSize: '10px', color: 'var(--muted)', 
            marginTop: '4px', textOverflow: 'ellipsis', 
            overflow: 'hidden', whiteSpace: 'nowrap' 
          }} title={roleArn}>
            Role: {roleArn}
          </div>
        )}
      </div>

      {/* Logout */}
      <button onClick={handleLogout} className="btn btn-outline" style={{ width: '100%' }}>
        ⇥ Logout
      </button>
    </aside>
  )
}








// 
// 
// import { NavLink, useNavigate } from 'react-router-dom'
// import useAuthStore from '../store/useAuthStore'

// const links = [
//   { to: '/dashboard',        icon: '▦', label: 'Dashboard' },
//   { to: '/resources',        icon: '⬡', label: 'Resources' },
//   { to: '/recommendations',  icon: '◈', label: 'Recommendations' },
//   { to: '/connect',          icon: '⊕', label: 'Connect Account' },
// ]

// export default function Sidebar() {
//   const logout = useAuthStore((s) => s.logout)
//   const navigate = useNavigate()

//   const handleLogout = () => {
//     logout()
//     navigate('/login')
//   }

//   return (
//     <aside style={{
//       position: 'fixed', top: 0, left: 0,
//       width: '240px', height: '100vh',
//       background: 'var(--bg2)',
//       borderRight: '1px solid var(--border)',
//       display: 'flex', flexDirection: 'column',
//       padding: '24px 16px', zIndex: 100,
//     }}>
//       {/* Logo */}
//       <div style={{ marginBottom: '40px', paddingLeft: '8px' }}>
//         <div style={{
//           fontFamily: 'Syne', fontSize: '18px',
//           fontWeight: 800, color: 'var(--accent)',
//           letterSpacing: '-0.5px',
//         }}>
//           ◉ CloudOpt
//         </div>
//         <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px' }}>
//           Cost Optimizer
//         </div>
//       </div>

//       {/* Nav links */}
//       <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
//         {links.map((l) => (
//           <NavLink
//             key={l.to}
//             to={l.to}
//             style={({ isActive }) => ({
//               display: 'flex', alignItems: 'center', gap: '12px',
//               padding: '10px 12px', borderRadius: '10px',
//               fontSize: '14px', fontWeight: 500,
//               textDecoration: 'none',
//               color: isActive ? 'var(--accent)' : 'var(--muted)',
//               background: isActive ? 'rgba(0,212,170,0.08)' : 'transparent',
//               transition: 'all 0.2s',
//             })}
//           >
//             <span style={{ fontSize: '16px' }}>{l.icon}</span>
//             {l.label}
//           </NavLink>
//         ))}
//       </nav>

//       {/* Logout */}
//       <button onClick={handleLogout} className="btn btn-outline" style={{ width: '100%' }}>
//         ⇥ Logout
//       </button>
//     </aside>
//   )
// }