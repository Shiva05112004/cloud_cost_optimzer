import { useState, useRef, useEffect } from 'react'
import useChatStore from '../store/useChatStore'
import { askCloudOpt } from '../api/chat.api'
import ChatBubble from './ChatBubble'

export default function ChatBox({ rec }) {
  const instanceId = rec.instance_id
  const [input, setInput] = useState('')
  const scrollRef = useRef(null)

  const {
    openId, loadingId, toggleChat,
    sendMessage, receiveAnswer, receiveError, getThread,
  } = useChatStore()

  const isOpen   = openId === instanceId
  const isLoading = loadingId === instanceId
  const thread   = getThread(instanceId)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [thread, isLoading])

  const handleAsk = async (question) => {
    if (!question.trim()) return
    sendMessage(instanceId, question)
    setInput('')

    const awsContext = {
      instance_id: rec.instance_id,
      instance_type: rec.recommended_type || rec.instance_type,
      avg_cpu: rec.avg_cpu,
      monthly_cost: rec.current_cost,
      z_score: rec.z_score || null,
      recommendation: rec.action,
    }

    try {
      const res = await askCloudOpt(question, awsContext)
      receiveAnswer(instanceId, res.data.answer)
    } catch {
      receiveError(instanceId)
    }
  }

  const suggestedQuestions = [
    'Why is this flagged?',
    'What happens if I stop it?',
    'Is this safe to apply?',
  ]

  return (
    <div style={{ marginTop: '12px' }}>
      <button
        onClick={() => toggleChat(instanceId)}
        style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          background: 'transparent', border: 'none', cursor: 'pointer',
          color: 'var(--accent)', fontSize: '12px', fontWeight: 600,
          padding: '6px 0',
        }}
      >
        💬 {isOpen ? 'Hide chat' : 'Ask CloudOpt about this'}
      </button>

      {isOpen && (
        <div style={{
          background: 'var(--bg3)', borderRadius: '12px',
          padding: '12px', marginTop: '8px',
        }}>
          {/* Message thread */}
          <div
            ref={scrollRef}
            style={{ maxHeight: '220px', overflowY: 'auto', marginBottom: '10px' }}
          >
            {thread.length === 0 && (
              <p style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '8px' }}>
                Ask a question about this instance — grounded in AWS docs and live data.
              </p>
            )}
            {thread.map((msg, i) => (
              <ChatBubble key={i} role={msg.role} text={msg.text} />
            ))}
            {isLoading && (
              <div style={{ fontSize: '12px', color: 'var(--muted)', padding: '4px 0' }}>
                CloudOpt is thinking...
              </div>
            )}
          </div>

          {/* Suggested questions — only show before first message */}
          {thread.length === 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '10px' }}>
              {suggestedQuestions.map((q) => (
                <button
                  key={q}
                  onClick={() => handleAsk(q)}
                  style={{
                    fontSize: '11px', padding: '5px 10px',
                    borderRadius: '20px', border: '1px solid var(--border)',
                    background: 'transparent', color: 'var(--muted)',
                    cursor: 'pointer',
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Input row */}
          <form
            onSubmit={(e) => { e.preventDefault(); handleAsk(input) }}
            style={{ display: 'flex', gap: '8px' }}
          >
            <input
              className="input"
              placeholder="Type your question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              style={{ flex: 1, padding: '8px 12px', fontSize: '13px' }}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="btn btn-primary"
              style={{ padding: '8px 16px' }}
              disabled={isLoading || !input.trim()}
            >
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  )
}