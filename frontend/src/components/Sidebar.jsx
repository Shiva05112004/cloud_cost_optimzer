import { NavLink, useNavigate } from 'react-router-dom'
import useAuthStore from '../store/useAuthStore'
import AwsConnectionStatus from './AwsConnectionStatus'

const links = [
  { to: '/dashboard',        icon: '▦', label: 'Dashboard' },
  { to: '/resources',        icon: '⬡', label: 'Resources' },
  { to: '/recommendations',  icon: '◈', label: 'Recommendations' },
  { to: '/connect',          icon: '⊕', label: 'Connect Account' },
]

export default function Sidebar() {
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

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
    }}>
      {/* Logo */}
      <div style={{ marginBottom: '24px', paddingLeft: '8px' }}>
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

      {/* AWS Connection Status */}
      <div style={{ marginBottom: '24px' }}>
        <AwsConnectionStatus />
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

      {/* Logout */}
      <button onClick={handleLogout} className="btn btn-outline" style={{ width: '100%' }}>
        ⇥ Logout
      </button>
    </aside>
  )
}