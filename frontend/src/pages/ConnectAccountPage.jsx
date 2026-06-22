import { useState } from 'react'
import { connectAccount } from '../api/accounts.api'
import toast from 'react-hot-toast'

export default function ConnectAccountPage() {
  const [form, setForm] = useState({ account_name: '', role_arn: '' })
  const [loading, setLoading] = useState(false)
  const [connected, setConnected] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await connectAccount(form)
      toast.success('AWS account connected!')
      // Persist the connected role ARN so other pages can use it
      try { localStorage.setItem('connected_role_arn', form.role_arn) } catch (error) { console.error('Failed to save role ARN in localStorage', error) }
      setConnected(true)
    } catch {
      toast.error('Failed to connect account.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="page-title">Connect AWS Account</h1>
      <p className="page-sub">Provide your IAM Role ARN to start analysing costs</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Form */}
        <div className="card">
          {connected
            ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>✦</div>
                <h3 style={{ fontFamily: 'Syne', marginBottom: '8px', color: 'var(--accent)' }}>Connected!</h3>
                <p style={{ color: 'var(--muted)', fontSize: '14px' }}>
                  Head to Dashboard to see your insights.
                </p>
              </div>
            )
            : (
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <label className="label">Account Name</label>
                  <input className="input" placeholder="My Company AWS"
                    value={form.account_name}
                    onChange={(e) => setForm({ ...form, account_name: e.target.value })} required />
                </div>
                <div>
                  <label className="label">IAM Role ARN</label>
                  <input className="input"
                    placeholder="arn:aws:iam::123456789012:role/CloudOptimizerRole"
                    value={form.role_arn}
                    onChange={(e) => setForm({ ...form, role_arn: e.target.value })} required />
                </div>
                <button className="btn btn-primary" type="submit"
                  style={{ justifyContent: 'center', padding: '13px' }}
                  disabled={loading}>
                  {loading ? 'Connecting...' : 'Connect Account →'}
                </button>
              </form>
            )
          }
        </div>

        {/* Instructions */}
        <div className="card">
          <h3 style={{ fontFamily: 'Syne', fontSize: '16px', marginBottom: '20px' }}>
            How to set up IAM Role
          </h3>
          {[
            { step: '01', text: 'Go to AWS Console → IAM → Roles → Create Role' },
            { step: '02', text: 'Select "Another AWS Account" and enter our App Account ID' },
            { step: '03', text: 'Attach: AmazonEC2ReadOnlyAccess + CloudWatchReadOnlyAccess + AWSCostExplorerReadOnlyAccess' },
            { step: '04', text: 'Name your role and copy the Role ARN' },
            { step: '05', text: 'Paste the Role ARN in the form and click Connect' },
          ].map((item) => (
            <div key={item.step} style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
              <div style={{
                minWidth: '32px', height: '32px', borderRadius: '8px',
                background: 'rgba(0,212,170,0.1)', color: 'var(--accent)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '11px', fontWeight: 700, fontFamily: 'Syne',
              }}>
                {item.step}
              </div>
              <p style={{ fontSize: '13px', color: 'var(--muted)', lineHeight: 1.6, paddingTop: '6px' }}>
                {item.text}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}