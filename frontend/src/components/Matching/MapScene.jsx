/**
 * 智慧媒合場景（/map）
 * 左側：供方選擇 + 媒合結果清單
 * 右側：Leaflet 地圖
 */
import { useState, useEffect } from 'react'
import LeafletMap from './LeafletMap'
import MatchCard from './MatchCard'
import { matchApi } from '../../services/api'

export default function MapScene() {
  const [sites,          setSites]          = useState([])
  const [supplySites,    setSupplySites]    = useState([])
  const [selectedSupply, setSelectedSupply] = useState(null)
  const [matchResults,   setMatchResults]   = useState([])
  const [isLoading,      setIsLoading]      = useState(false)
  const [error,          setError]          = useState(null)
  const [useDemo,        setUseDemo]        = useState(true)

  // 載入工地資料（Demo 或 DB）
  useEffect(() => {
    loadSites()
  }, [useDemo])

  async function loadSites() {
    setError(null)
    try {
      if (useDemo) {
        // 優先嘗試後端 DB
        const res = await matchApi.getSites()
        if (res.sites && res.sites.length > 0) {
          setSites(res.sites)
          setSupplySites(res.sites.filter(s => s.role === 'supply'))
        } else {
          // 後端無資料，用 Demo JSON
          const demo = await matchApi.getDemo()
          setSites(demo.sites || [])
          setSupplySites((demo.sites || []).filter(s => s.role === 'supply'))
        }
      }
    } catch (err) {
      // 後端離線，嘗試 Demo endpoint
      try {
        const demo = await matchApi.getDemo()
        setSites(demo.sites || [])
        setSupplySites((demo.sites || []).filter(s => s.role === 'supply'))
      } catch {
        setError('無法載入工地資料，請確認後端服務是否啟動')
      }
    }
  }

  // 執行媒合
  async function handleRunMatch() {
    if (!selectedSupply) return
    setIsLoading(true)
    setMatchResults([])
    setError(null)
    try {
      const res = await matchApi.runMatch(selectedSupply.id, 5, { max_distance_km: 50 })
      setMatchResults(res.matches || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  // 地圖用的媒合結果（含座標）
  const mapMatches = matchResults.map(m => ({
    ...m,
    lat: sites.find(s => s.id === m.site_id)?.lat || m.lat,
    lng: sites.find(s => s.id === m.site_id)?.lng || m.lng,
  }))

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '360px 1fr',
      height: 'calc(100vh - var(--nav-h))',
      overflow: 'hidden',
    }}>
      {/* ── 左側側欄 ── */}
      <div style={{
        background: 'var(--surface)',
        borderRight: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column', overflow: 'hidden',
      }}>
        {/* 頁首 */}
        <div style={{ padding: '16px 20px 13px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
          <div className="module-tag" style={{ marginBottom: 7 }}>◉ AI · 智慧媒合</div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-hi)', marginBottom: 2 }}>
            智慧供需配對
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted2)' }}>
            選擇供方工地，AI 計算最佳媒合目標
          </div>
        </div>

        {/* 工地選擇 */}
        <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.7px', marginBottom: 8 }}>
            選擇供方工地
          </div>
          {supplySites.length === 0 ? (
            <div style={{ fontSize: 12, color: 'var(--muted)', textAlign: 'center', padding: '12px 0' }}>
              載入中...
            </div>
          ) : (
            supplySites.map(site => (
              <div
                key={site.id}
                onClick={() => { setSelectedSupply(site); setMatchResults([]) }}
                style={{
                  padding: '8px 10px',
                  borderRadius: 6,
                  border: `1px solid ${selectedSupply?.id === site.id ? 'var(--green-dim)' : 'var(--border)'}`,
                  background: selectedSupply?.id === site.id ? 'var(--green-glow)' : 'var(--surface2)',
                  marginBottom: 6,
                  cursor: 'pointer',
                  transition: 'all .15s',
                }}
              >
                <div style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-hi)', marginBottom: 3 }}>
                  {site.name}
                </div>
                <div style={{ fontSize: 11, color: 'var(--muted2)', display: 'flex', gap: 8 }}>
                  <span>{site.soil_code || site.soil_type}</span>
                  <span>{site.volume_m3?.toLocaleString()} m³</span>
                  {site.price_per_m3 && <span>NT${site.price_per_m3}/m³</span>}
                </div>
              </div>
            ))
          )}

          <button
            className="btn btn-primary"
            disabled={!selectedSupply || isLoading}
            onClick={handleRunMatch}
            style={{ width: '100%', marginTop: 8 }}
          >
            {isLoading ? '⟳ 計算中...' : '🤖 執行 AI 媒合'}
          </button>
        </div>

        {/* 錯誤提示 */}
        {error && (
          <div style={{
            margin: '10px 14px 0',
            padding: '8px 12px',
            background: 'rgba(248,113,113,.1)',
            border: '1px solid rgba(248,113,113,.25)',
            borderRadius: 6,
            fontSize: 11.5,
            color: 'var(--danger)',
          }}>
            ⚠ {error}
          </div>
        )}

        {/* 媒合結果清單 */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '12px 14px' }}>
          {matchResults.length > 0 && (
            <>
              <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.7px', marginBottom: 8 }}>
                媒合結果（{matchResults.length} 筆）
              </div>
              {matchResults.map((m, i) => (
                <MatchCard
                  key={m.site_id}
                  match={m}
                  rank={i}
                  onClick={() => {}}
                />
              ))}

              {/* 效益統計 */}
              <div style={{
                display: 'flex', gap: 0,
                background: 'var(--green-glow2)',
                border: '1px solid var(--green-dim)',
                borderRadius: 7, overflow: 'hidden',
                marginTop: 10,
              }}>
                {[
                  { num: matchResults.length, label: '配對成功' },
                  { num: `${Math.min(...matchResults.map(m => m.distance_km))} km`, label: '最近距離' },
                  { num: `${Math.max(...matchResults.map(m => m.score)).toFixed(0)}`, label: '最高評分' },
                ].map((b, i) => (
                  <div key={i} style={{
                    flex: 1, padding: '10px 6px', textAlign: 'center',
                    borderRight: i < 2 ? '1px solid var(--green-dim)' : 'none',
                  }}>
                    <div style={{ fontFamily: "'Fraunces',serif", fontSize: 20, color: 'var(--green)', lineHeight: 1 }}>{b.num}</div>
                    <div style={{ fontSize: 10, color: 'var(--muted2)', marginTop: 2 }}>{b.label}</div>
                  </div>
                ))}
              </div>
            </>
          )}

          {matchResults.length === 0 && !isLoading && selectedSupply && (
            <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--muted)', fontSize: 12 }}>
              點擊「執行 AI 媒合」開始計算
            </div>
          )}

          {!selectedSupply && (
            <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--muted)', fontSize: 12 }}>
              請先選擇供方工地
            </div>
          )}
        </div>
      </div>

      {/* ── 右側地圖 ── */}
      <div style={{ position: 'relative', overflow: 'hidden', background: '#080d08' }}>
        <LeafletMap
          sites={sites}
          selectedSupplyId={selectedSupply?.id}
          matches={mapMatches}
        />

        {/* 圖例 */}
        <div style={{
          position: 'absolute', bottom: 68, left: 14, zIndex: 500,
          background: 'rgba(13,18,16,.92)', border: '1px solid var(--border)',
          borderRadius: 8, padding: '10px 13px', backdropFilter: 'blur(8px)',
        }}>
          <div style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: 1, textTransform: 'uppercase', marginBottom: 7, fontFamily: "'DM Mono',monospace" }}>
            圖例
          </div>
          {[
            { color: '#ef4444', label: '供方（出土）' },
            { color: '#4ade80', label: '需方（填土）' },
            { color: '#fbbf24', label: '土資場' },
          ].map(item => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 11, color: 'var(--text)', marginBottom: 4 }}>
              <div style={{ width: 9, height: 9, borderRadius: '50%', background: item.color, flexShrink: 0 }} />
              {item.label}
            </div>
          ))}
        </div>

        {/* 統計覆蓋層 */}
        <div style={{
          position: 'absolute', top: 12, left: 12, zIndex: 500,
          display: 'flex', gap: 8, flexWrap: 'wrap', pointerEvents: 'none',
        }}>
          {[
            { label: '供方', val: sites.filter(s => s.role === 'supply').length },
            { label: '需方', val: sites.filter(s => s.role === 'demand').length },
            { label: '土資場', val: sites.filter(s => s.role === 'dump').length },
          ].map(stat => (
            <div key={stat.label} style={{
              background: 'rgba(13,18,16,.92)', border: '1px solid var(--border)',
              borderRadius: 8, padding: '8px 12px', backdropFilter: 'blur(8px)',
              pointerEvents: 'all',
            }}>
              <div style={{ fontFamily: "'DM Mono',monospace", fontSize: 9, color: 'var(--muted)', letterSpacing: 1, textTransform: 'uppercase', marginBottom: 2 }}>
                {stat.label}
              </div>
              <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--green)', lineHeight: 1.1 }}>
                {stat.val}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
