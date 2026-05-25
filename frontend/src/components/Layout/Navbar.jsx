import { useNavigate, useLocation } from 'react-router-dom'

const TABS = [
  { path: '/',         icon: '◈', label: '首頁' },
  { path: '/chat',     icon: '⬡', label: '法規問答' },
  { path: '/map',      icon: '◉', label: '智慧媒合' },
  { path: '/manifest', icon: '▦', label: '電子聯單' },
]

export default function Navbar() {
  const navigate  = useNavigate()
  const location  = useLocation()

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 999,
      display: 'flex', alignItems: 'center',
      background: 'rgba(13,18,16,.96)',
      borderBottom: '1px solid var(--border)',
      backdropFilter: 'blur(16px)',
      padding: '0 28px',
      height: 'var(--nav-h)',
      gap: '8px',
    }}>
      {/* Logo */}
      <div
        onClick={() => navigate('/')}
        style={{ display: 'flex', alignItems: 'center', gap: 10, marginRight: 28, cursor: 'pointer' }}
      >
        <div style={{
          width: 30, height: 30,
          background: 'var(--green-glow)',
          border: '1px solid var(--green-dim)',
          borderRadius: 7,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 14,
        }}>🌱</div>
        <span style={{ fontFamily: "'Fraunces',serif", fontSize: 17, color: 'var(--text-hi)', letterSpacing: '-.3px' }}>
          Tu<em style={{ color: 'var(--green)', fontStyle: 'normal' }}>Flow</em>
        </span>
      </div>

      {/* 導覽標籤 */}
      <div style={{ display: 'flex', gap: 2 }}>
        {TABS.map(tab => {
          const isActive = location.pathname === tab.path
          return (
            <button
              key={tab.path}
              onClick={() => navigate(tab.path)}
              style={{
                padding: '6px 14px',
                borderRadius: 6,
                fontSize: 13,
                fontWeight: 500,
                cursor: 'pointer',
                border: `1px solid ${isActive ? 'var(--green-dim)' : 'transparent'}`,
                color: isActive ? 'var(--green)' : 'var(--muted2)',
                background: isActive ? 'var(--green-glow)' : 'transparent',
                display: 'flex', alignItems: 'center', gap: 6,
                transition: 'all .18s',
                whiteSpace: 'nowrap',
              }}
            >
              <span style={{ fontSize: 10 }}>{tab.icon}</span>
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* 右側版本號 */}
      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{
          fontFamily: "'DM Mono',monospace",
          fontSize: 10,
          color: 'var(--muted)',
          background: 'var(--surface2)',
          border: '1px solid var(--border)',
          padding: '4px 10px',
          borderRadius: 20,
        }}>v1.0 DEMO</span>
      </div>
    </nav>
  )
}
