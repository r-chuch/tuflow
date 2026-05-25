import { useNavigate } from 'react-router-dom'

const FEATURES = [
  {
    icon: '⬡',
    tag: 'RAG · 法規問答',
    title: '即時法規諮詢',
    desc: '輸入問題，AI 依法條精準回答，附帶條文原文引用，縮短合規查詢時間 70%',
    cta: '開始諮詢',
    path: '/chat',
    color: 'var(--amber)',
    glow: 'var(--amber-glow)',
    dim: 'rgba(251,191,36,.2)',
  },
  {
    icon: '◉',
    tag: 'AI · 智慧媒合',
    title: '供需智慧配對',
    desc: '多維評分演算法即時配對最近、最合適的清運目標，媒合效率提升 70%',
    cta: 'AI 媒合地圖',
    path: '/map',
    color: 'var(--green)',
    glow: 'var(--green-glow)',
    dim: 'var(--green-dim)',
  },
  {
    icon: '▦',
    tag: 'NLP · 自動填單',
    title: '一句話填聯單',
    desc: '語音或文字輸入，自動擷取身份證、車牌、出土量，人工錯誤減少 80%',
    cta: '開始填單',
    path: '/manifest',
    color: 'var(--blue)',
    glow: 'var(--blue-glow)',
    dim: 'rgba(96,165,250,.2)',
  },
]

const STATS = [
  { num: '3,600', unit: '萬 m³', label: '台灣每年廢土產出' },
  { num: '70%',   unit: '',       label: '合規查詢時間縮短' },
  { num: '15-30%',unit: '',       label: '清運成本降低' },
  { num: '80%',   unit: '',       label: '人工填單錯誤減少' },
]

export default function HeroSection() {
  const navigate = useNavigate()

  return (
    <div style={{ minHeight: 'calc(100vh - var(--nav-h))', background: 'var(--bg)', overflowY: 'auto' }}>
      {/* Hero */}
      <section style={{ padding: '72px 48px 48px', maxWidth: 900, margin: '0 auto', textAlign: 'center' }}>
        <div className="module-tag" style={{ marginBottom: 20 }}>
          🌱 TuFlow 土不落 · AI 智慧土方循環管理
        </div>
        <h1 style={{
          fontFamily: "'Fraunces',serif",
          fontSize: 52,
          color: 'var(--text-hi)',
          lineHeight: 1.15,
          marginBottom: 20,
        }}>
          讓廢土成為<br/>
          <span style={{ color: 'var(--green)' }}>可流通的資源</span>
        </h1>
        <p style={{ fontSize: 15, color: 'var(--muted2)', lineHeight: 1.8, marginBottom: 36, maxWidth: 560, margin: '0 auto 36px' }}>
          台灣每年產出 3,600～4,200 萬立方公尺廢土，TuFlow 以 AI 打造去中心化虛擬調度系統，
          從法規合規、供需媒合到電子聯單，全流程智慧管理。
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/map')}>
            🗺 開始 AI 媒合
          </button>
          <button className="btn btn-ghost btn-lg" onClick={() => navigate('/chat')}>
            ⬡ 法規諮詢
          </button>
        </div>
      </section>

      {/* 數據統計 */}
      <section style={{
        display: 'flex', gap: 0, maxWidth: 700, margin: '0 auto 56px',
        background: 'var(--green-glow2)',
        border: '1px solid var(--green-dim)',
        borderRadius: 10, overflow: 'hidden',
      }}>
        {STATS.map((s, i) => (
          <div key={i} style={{
            flex: 1, padding: '16px 8px', textAlign: 'center',
            borderRight: i < STATS.length - 1 ? '1px solid var(--green-dim)' : 'none',
          }}>
            <div style={{ fontFamily: "'Fraunces',serif", fontSize: 24, color: 'var(--green)', lineHeight: 1 }}>
              {s.num}<span style={{ fontSize: 13 }}>{s.unit}</span>
            </div>
            <div style={{ fontSize: 10, color: 'var(--muted2)', marginTop: 4, lineHeight: 1.3 }}>{s.label}</div>
          </div>
        ))}
      </section>

      {/* 功能卡片 */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16, maxWidth: 960, margin: '0 auto', padding: '0 24px 72px' }}>
        {FEATURES.map((f) => (
          <div key={f.path} style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 12, padding: 24,
            display: 'flex', flexDirection: 'column', gap: 14,
            transition: 'border-color .2s',
          }}
            onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-hi)'}
            onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
          >
            <div style={{
              width: 40, height: 40,
              background: f.glow,
              border: `1px solid ${f.dim}`,
              borderRadius: 10,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18,
            }}>
              <span style={{ color: f.color }}>{f.icon}</span>
            </div>
            <div>
              <div style={{ fontSize: 10, color: f.color, fontFamily: "'DM Mono',monospace", letterSpacing: 1, marginBottom: 6 }}>
                {f.tag}
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-hi)', marginBottom: 8 }}>{f.title}</h3>
              <p style={{ fontSize: 12, color: 'var(--muted2)', lineHeight: 1.7 }}>{f.desc}</p>
            </div>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => navigate(f.path)}
              style={{ alignSelf: 'flex-start', marginTop: 'auto' }}
            >
              {f.cta} →
            </button>
          </div>
        ))}
      </section>
    </div>
  )
}
