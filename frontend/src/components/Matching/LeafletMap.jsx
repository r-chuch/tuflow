/**
 * Leaflet 地圖元件（react-leaflet）
 * 顯示供方工地、需方工地、連線
 */
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline, useMap } from 'react-leaflet'
import { useEffect } from 'react'

// 地圖中心：桃園市
const TAOYUAN_CENTER = [24.993, 121.310]

// 圓點顏色設定
const MARKER_COLORS = {
  supply: '#4ade80',   // 綠色：供方
  demand: '#60a5fa',   // 藍色：需方
  dump:   '#fbbf24',   // 琥珀：土資場
  selected: '#4ade80', // 選中（高亮）
}

// ── 自動縮放至所有工地 ──────────────────────────────────────────
function AutoFit({ sites }) {
  const map = useMap()
  useEffect(() => {
    if (!sites || sites.length === 0) return
    const bounds = sites.map(s => [s.lat, s.lng])
    if (bounds.length > 0) map.fitBounds(bounds, { padding: [40, 40] })
  }, [sites, map])
  return null
}

export default function LeafletMap({ sites = [], selectedSupplyId, selectedMatchId, matches = [] }) {
  // 找到選中的供方 & 媒合的需方
  const supplySite  = sites.find(s => s.id === selectedSupplyId)
  const matchedIds  = matches.map(m => m.site_id)

  return (
    <MapContainer
      center={TAOYUAN_CENTER}
      zoom={11}
      style={{ width: '100%', height: '100%' }}
      zoomControl={false}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='© OpenStreetMap'
      />
      <AutoFit sites={sites} />

      {/* 供方 → 選中媒合目標的連線 */}
      {supplySite && matches.map((m, i) => (
        <Polyline
          key={`line-${i}`}
          positions={[[supplySite.lat, supplySite.lng], [m.lat, m.lng]]}
          pathOptions={{
            color: i === 0 ? '#4ade80' : '#28352a',
            weight: i === 0 ? 2 : 1,
            dashArray: i === 0 ? null : '4 4',
            opacity: i === 0 ? 0.9 : 0.4,
          }}
        />
      ))}

      {/* 工地圓點 */}
      {sites.map(site => {
        const isSupply   = site.role === 'supply'
        const isSelected = site.id === selectedSupplyId
        const isMatched  = matchedIds.includes(site.id)
        const color = MARKER_COLORS[site.role] || '#7a9b7d'
        const radius = isSelected ? 10 : isMatched ? 8 : 6

        return (
          <CircleMarker
            key={site.id}
            center={[site.lat, site.lng]}
            radius={radius}
            pathOptions={{
              color:       isSelected ? '#fff' : color,
              fillColor:   color,
              fillOpacity: 0.85,
              weight:      isSelected ? 2 : 1,
            }}
          >
            <Popup>
              <div style={{
                fontFamily: "'Noto Sans TC', sans-serif",
                fontSize: 12,
                lineHeight: 1.6,
                color: '#1a1a1a',
                minWidth: 160,
              }}>
                <div style={{ fontWeight: 700, marginBottom: 4 }}>{site.name}</div>
                <div>角色：{site.role === 'supply' ? '🟢 供方' : site.role === 'demand' ? '🔵 需方' : '🟡 土資場'}</div>
                <div>土質：{site.soil_code || site.soil_type}</div>
                <div>數量：{site.volume_m3?.toLocaleString()} m³</div>
                {site.price_per_m3 && <div>單價：NT$ {site.price_per_m3}/m³</div>}
                {site.address && <div style={{ marginTop: 4, color: '#666', fontSize: 11 }}>{site.address}</div>}
              </div>
            </Popup>
          </CircleMarker>
        )
      })}
    </MapContainer>
  )
}
