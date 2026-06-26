export default function ChatBubble({ role, text }) {
  const isUser = role === 'user'
  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '10px',
    }}>
      <div style={{
        maxWidth: '85%',
        padding: '10px 14px',
        borderRadius: isUser ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
        background: isUser ? 'var(--accent)' : 'var(--bg3)',
        color: isUser ? '#0a0f1e' : 'var(--text)',
        fontSize: '13px',
        lineHeight: 1.5,
      }}>
        {!isUser && (
          <div style={{
            fontSize: '10px', fontWeight: 700, color: 'var(--accent)',
            marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em',
          }}>
            CloudOpt
          </div>
        )}
        {text}
      </div>
    </div>
  )
}