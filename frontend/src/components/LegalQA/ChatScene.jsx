/**
 * 法規問答場景（/chat）
 * 左側：對話訊息
 * 右側：法規資料庫狀態 + 快速問題
 */
import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ChatMessage from './ChatMessage'
import { ragApi } from '../../services/api'

// 預設快速問題
const QUICK_PROMPTS = [
  '桃園土石方要怎麼申報？',
  '違法棄土會有什麼罰則？',
  '聯單申報數量和實際出土量有誤差怎麼辦？',
  '在山坡地堆置土石方需要什麼許可？',
]

// Demo QA 快取（後端未啟動時使用，從 public/demo_qa.json 載入）
let _demoQA = null
async function getDemoQA() {
  if (!_demoQA) {
    const res = await fetch('/demo_qa.json')
    _demoQA = await res.json()
  }
  return _demoQA
}

export default function ChatScene() {
  const navigate = useNavigate()
  const [messages,  setMessages]  = useState([
    {
      role: 'ai',
      text: '您好！我是 TuFlow 法規助理 🌱\n\n我可以幫您查詢台灣營建剩餘土石方相關法規，包括桃園市自治條例、廢棄物清理法、水土保持法等。請直接提問！',
    }
  ])
  const [input,     setInput]     = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [ragStatus, setRagStatus] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 載入 RAG 狀態
  useEffect(() => {
    ragApi.getStatus().then(setRagStatus).catch(() => {})
  }, [])

  async function handleSend(question) {
    const q = (question || input).trim()
    if (!q) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: q }])
    setMessages(prev => [...prev, { role: 'ai', isTyping: true, text: '' }])
    setIsLoading(true)

    try {
      const res = await ragApi.query(q)
      setMessages(prev => {
        const next = [...prev]
        next[next.length - 1] = {
          role: 'ai',
          text: res.answer,
          lawRefs: res.law_refs || [],
          confidence: res.confidence,
          suggestedAction: res.suggested_action,
        }
        return next
      })
    } catch (err) {
      // 後端離線或 LLM 失敗 → 嘗試 Demo 資料
      console.warn('[TuFlow] RAG query failed:', err.message)
      const demoData = await getDemoQA().catch(() => [])
      const demo = demoData.find(d =>
        q.includes(d.question.slice(0, 6)) || d.question.includes(q.slice(0, 6))
      )

      // 判斷失敗類型給使用者更清楚的提示
      let fallbackNote = ''
      if (err.message?.includes('GROQ_API_KEY')) {
        fallbackNote = '\n\n⚠️ 後端 GROQ_API_KEY 未設定，請檢查 .env 並重啟後端。'
      } else if (err.message?.includes('fetch') || err.message?.includes('Failed')) {
        fallbackNote = '\n\n⚠️ 無法連接後端（port 8001），請確認後端已啟動。'
      } else if (err.message) {
        fallbackNote = `\n\n⚠️ 後端錯誤：${err.message}`
      }

      setMessages(prev => {
        const next = [...prev]
        next[next.length - 1] = {
          role: 'ai',
          text: demo
            ? demo.answer + (fallbackNote ? `\n\n---\n📋 以上為示範資料${fallbackNote}` : '')
            : `抱歉，目前無法取得 AI 回應。${fallbackNote}\n\n啟動後端：\nuvicorn backend.main:app --reload --port 8001`,
          lawRefs: demo?.law_refs || [],
          confidence: demo?.confidence,
          suggestedAction: demo?.suggested_action,
          isDemo: true,
        }
        return next
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr 300px',
      height: 'calc(100vh - var(--nav-h))',
      overflow: 'hidden',
    }}>
      {/* ── 左側：對話區 ── */}
      <div style={{
        display: 'flex', flexDirection: 'column',
        background: 'var(--surface)',
        borderRight: '1px solid var(--border)',
        overflow: 'hidden',
      }}>
        {/* 頁首 */}
        <div style={{ padding: '16px 20px 13px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
          <div className="module-tag" style={{ marginBottom: 7 }}>⬡ RAG · 法規問答</div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-hi)', marginBottom: 2 }}>
            即時法規諮詢
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted2)' }}>
            AI 根據法條精準回答，附帶原文引用
          </div>
        </div>

        {/* 訊息區 */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 12 }}>
          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* 快速問題 */}
        <div style={{ padding: '8px 14px 0', flexShrink: 0 }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 8 }}>
            {QUICK_PROMPTS.map(q => (
              <button
                key={q}
                onClick={() => handleSend(q)}
                disabled={isLoading}
                style={{
                  fontSize: 11, padding: '4px 9px', borderRadius: 20,
                  border: '1px solid var(--border)',
                  color: 'var(--muted2)', cursor: 'pointer',
                  background: 'transparent', transition: 'all .18s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor = 'var(--green-dim)'
                  e.currentTarget.style.color = 'var(--green)'
                  e.currentTarget.style.background = 'var(--green-glow)'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor = 'var(--border)'
                  e.currentTarget.style.color = 'var(--muted2)'
                  e.currentTarget.style.background = 'transparent'
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* 輸入區 */}
        <div style={{ padding: '0 14px 14px', flexShrink: 0 }}>
          <div style={{ display: 'flex', gap: 6, alignItems: 'flex-end' }}>
            <textarea
              className="form-input"
              placeholder="輸入您的法規問題..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              rows={2}
              style={{ flex: 1, resize: 'none' }}
            />
            <button
              className="btn btn-primary"
              onClick={() => handleSend()}
              disabled={isLoading || !input.trim()}
              style={{ padding: '8px 13px', fontSize: 15, lineHeight: 1, flexShrink: 0 }}
            >
              ↑
            </button>
          </div>
          <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 4 }}>
            Enter 送出 · Shift+Enter 換行
          </div>
        </div>
      </div>

      {/* ── 右側：狀態面板 ── */}
      <div style={{
        background: 'var(--bg)',
        display: 'flex', flexDirection: 'column', gap: 12,
        padding: 16, overflowY: 'auto',
      }}>
        {/* RAG 狀態 */}
        <div style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 8, padding: 14,
        }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.7px', marginBottom: 10 }}>
            法規資料庫狀態
          </div>
          {ragStatus ? (
            <>
              {/* 已載入條文數 */}
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, padding: '4px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ color: 'var(--muted2)' }}>已載入條文</span>
                <span style={{ color: 'var(--green)', fontWeight: 600 }}>{ragStatus.doc_count} 條</span>
              </div>

              {/* LLM 答案生成模型 */}
              <div style={{ padding: '6px 0 2px' }}>
                <div style={{ fontSize: 9, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.5px', marginBottom: 3 }}>
                  LLM · 答案生成
                </div>
                <div style={{ fontSize: 10, color: 'var(--amber)', fontFamily: "'DM Mono',monospace", background: 'rgba(251,191,36,.07)', borderRadius: 4, padding: '3px 6px' }}>
                  {ragStatus.llm_model || 'llama-3.3-70b-versatile'}
                </div>
              </div>

              {/* 嵌入向量模型 */}
              <div style={{ padding: '4px 0 6px', borderBottom: '1px solid var(--border)' }}>
                <div style={{ fontSize: 9, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.5px', marginBottom: 3 }}>
                  Embedding · 語意檢索
                </div>
                <div style={{ fontSize: 10, color: 'var(--muted2)', fontFamily: "'DM Mono',monospace", background: 'var(--surface)', borderRadius: 4, padding: '3px 6px', border: '1px solid var(--border)' }}>
                  {ragStatus.embed_model || ragStatus.model?.split('/').pop() || 'mpnet-base-v2'}
                </div>
              </div>

              {/* 已載入法規 */}
              <div style={{ marginTop: 4 }}>
                {(ragStatus.laws_loaded || []).map(law => (
                  <div key={law} style={{ fontSize: 10.5, color: 'var(--muted2)', padding: '3px 0', display: 'flex', gap: 5 }}>
                    <span style={{ color: 'var(--green)' }}>✓</span> {law}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{ fontSize: 11, color: 'var(--muted)', textAlign: 'center', padding: '8px 0' }}>
              後端未連接（使用 Demo 模式）
            </div>
          )}
        </div>

        {/* 快速跳轉 */}
        <div style={{
          background: 'var(--green-glow2)',
          border: '1px solid var(--green-dim)',
          borderRadius: 8, padding: 14,
        }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-hi)', marginBottom: 8 }}>
            需要辦理申報？
          </div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => navigate('/manifest')}
            style={{ width: '100%' }}
          >
            ▦ 前往電子聯單填報
          </button>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => navigate('/map')}
            style={{ width: '100%', marginTop: 6 }}
          >
            ◉ 尋找合法收容場所
          </button>
        </div>
      </div>
    </div>
  )
}
