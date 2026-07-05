import { useEffect, useState } from 'react'
import { getConnectionStatus } from '../api/accounts.api'
import toast from 'react-hot-toast'

export default function AwsConnectionStatus() {
  const [status, setStatus] = useState({ connected: false, account_count: 0, accounts: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await getConnectionStatus()
        setStatus(response.data)
      } catch (error) {
        console.error('Failed to fetch AWS connection status:', error)
        // Don't show toast for this, it's a background check
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
    
    // Refresh status every 30 seconds
    const interval = setInterval(fetchStatus, 30000)
    
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 12px',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '8px',
        fontSize: '12px',
        color: 'var(--muted)',
      }}>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: 'var(--muted)',
          animation: 'pulse 1.5s infinite',
        }} />
        Checking AWS status...
      </div>
    )
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 12px',
      background: status.connected 
        ? 'rgba(0,212,170,0.1)' 
        : 'rgba(255,99,71,0.1)',
      borderRadius: '8px',
      fontSize: '12px',
      color: status.connected ? 'var(--accent)' : 'var(--danger)',
      border: status.connected 
        ? '1px solid rgba(0,212,170,0.3)' 
        : '1px solid rgba(255,99,71,0.3)',
    }}>
      <div style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        background: status.connected ? 'var(--accent)' : 'var(--danger)',
        boxShadow: status.connected 
          ? '0 0 8px rgba(0,212,170,0.5)' 
          : '0 0 8px rgba(255,99,71,0.5)',
      }} />
      {status.connected 
        ? `${status.account_count} AWS Account${status.account_count > 1 ? 's' : ''} Connected`
        : 'No AWS Account Connected'
      }
    </div>
  )
}
