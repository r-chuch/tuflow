/**
 * 媒合結果卡片元件
 * 顯示工地名稱、距離、評分 breakdown 進度條
 */
export default function MatchCard({ match, rank, isSelected, onClick }) {
  const isBest = rank === 0
  const score = match.score || 0
  const breakdown = match.score_breakdown || {}

  return (
    <div
      onClick={() => onClick?.(match)}
      style={{
        background: isBest ? 'rgba(74,222,128,.04)' : 'var(--surface2)',
        border: `1px solid ${isSelected ? 'var(--green)' : isBest ? 'var(--green-dim)' : 'var(--border)'}`,
        borderRadius: 8,
        padding: '11px 13px',
        marginBottom: 7,
        cursor: 'pointer',
        transition: 'all .18s',
      }}
      onMouseEnter={e => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--border-hi)' }}
      onMouseLeave={e => { if (!isSelected) e.currentTarget.style.borderColor = isBest ? 'var(--green-dim)' : 'var(--border)' }}
    >
      {/* 標題列 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 7 }}>
        <div style={{
          width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
          background: isBest ? 'var(--green)' : 'var(--muted)',
        }} />
        <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-hi)', flex: 1 }}>
          {match.name}
        </span>
        <span style={{
          fontFamily: "'DM Mono',monospace", fontSize: 9, padding: '2px 6px', borderRadius: 3,
          background: isBest ? 'var(--green-glow)' : 'var(--surface3)',
          color: isBest ? 'var(--green)' : 'var(--muted2)',
          border: `1px solid ${isBest ? 'var(--green-dim)' : 'var(--border)'}`,
        }}>
          {isBest ? 'BEST' : `#${rank + 1}`}
        </span>
      </div>

      {/* 距離 / 土質 / 數量 */}
      <div style={{ display: 'flex', gap: 11, fontSize: 11, color: 'var(--muted2)', marginBottom: 8 }}>
        <span>📍 <strong style={{ color: 'var(--text)' }}>{match.distance_km} km</strong></span>
        <span>🪨 <strong style={{ color: 'var(--text)' }}>{match.soil_code || match.soil_type}</strong></span>
        <span>📦 <strong style={{ color: 'var(--text)' }}>{match.volume_available?.toLocaleString()} m³</strong></span>
        {match.price_per_m3 && (
          <span>💰 <strong style={{ color: 'var(--amber)' }}>NT$ {match.price_per_m3}/m³</strong></span>
        )}
      </div>

      {/* 評分進度條 */}
      <div>
        <div style={{ height: 3, background: 'var(--border)', borderRadius: 2, overflow: 'hidden', marginBottom: 3 }}>
          <div style={{
            height: '100%',
            width: `${score}%`,
            background: `linear-gradient(90deg, var(--green-dim) 0%, var(--green) 100%)`,
            borderRadius: 2,
            transition: 'width .9s ease',
          }} />
        </div>
        <div style={{ fontSize: 9, color: 'var(--muted)', display: 'flex', justifyContent: 'space-between' }}>
          <span>
            距離 {breakdown.distance?.toFixed(1)}
            {' · '}數量 {breakdown.quantity?.toFixed(1)}
            {' · '}土質 {breakdown.compat?.toFixed(1)}
          </span>
          <span style={{ fontFamily: "'DM Mono',monospace", color: 'var(--green)', fontWeight: 600 }}>
            {score.toFixed(1)} 分
          </span>
        </div>
      </div>
    </div>
  )
}
