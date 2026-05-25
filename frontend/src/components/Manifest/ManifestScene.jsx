/**
 * 電子聯單場景（/manifest）
 * 左側：A 類系統欄位（唯讀）
 * 右側：B 類 NLP 填入 + 語音輸入
 */
import { useState, useEffect } from 'react'
import VoiceInput from './VoiceInput'
import { formApi } from '../../services/api'

const STATUS_LABELS = {
  0: '未載運', 1: '已出場', 2: '收容端進場',
  3: '紙本上傳', 4: '異常', 5: '單退', 6: '批退', 9: '違規',
}

const DEMO_MANIFEST = {
  id: 'TY-20260001',
  manifest_number: 'AAAA1001-BBBB2001-B1-00000001',
  project_name: '桃園市中山路新建大樓工程',
  project_code: 'AAAA1001',
  disposal_site_code: 'BBBB2001',
  disposal_site_name: '八德區公園填方工程',
  soil_code: 'B1',
  total_volume_m3: 800,
  route_list: ['路線一', '路線二'],
  manifest_status: 0,
}

export default function ManifestScene() {
  const [systemFields,   setSystemFields]   = useState(DEMO_MANIFEST)
  const [extracted,      setExtracted]      = useState({})
  const [rawInput,       setRawInput]       = useState('')
  const [isExtracting,   setIsExtracting]   = useState(false)
  const [confidence,     setConfidence]     = useState({})
  const [missingFields,  setMissingFields]  = useState([])
  const [manifestId,     setManifestId]     = useState(null)
  const [isSubmitting,   setIsSubmitting]   = useState(false)
  const [submitDone,     setSubmitDone]     = useState(false)
  const [error,          setError]          = useState(null)

  // 語音轉文字後自動填入輸入框
  function handleVoiceTranscript(text) {
    setRawInput(prev => prev ? prev + ' ' + text : text)
  }

  // 提交自然語言 → AI 提取欄位
  async function handleExtract() {
    if (!rawInput.trim()) return
    setIsExtracting(true)
    setError(null)
    try {
      const res = await formApi.extract(rawInput, 'text', {
        project_code: systemFields.project_code,
        disposal_site_code: systemFields.disposal_site_code,
        soil_code: systemFields.soil_code,
        route_list: systemFields.route_list,
      })
      setExtracted(res.extracted || {})
      setConfidence(res.confidence || {})
      setMissingFields(res.missing_fields || [])
    } catch {
      // 後端離線時：簡易規則解析
      const parsed = simpleParse(rawInput)
      setExtracted(parsed)
      setConfidence(Object.fromEntries(Object.keys(parsed).map(k => [k, 0.8])))
      setMissingFields([])
    } finally {
      setIsExtracting(false)
    }
  }

  // 簡易正則解析（後端離線備用）
  function simpleParse(text) {
    const result = {}
    // 路線
    const routeMatch = text.match(/路線[一二三四五六七八九十\d]+/)
    if (routeMatch) result.route_name = routeMatch[0]
    // 體積
    const volMatch = text.match(/(\d+\.?\d*)\s*方/)
    if (volMatch) result.actual_volume_m3 = parseFloat(volMatch[1])
    // 身份證
    const idMatch = text.match(/[A-Z][12]\d{8}/)
    if (idMatch) result.driver_id = idMatch[0]
    // 車號
    const plates = text.match(/[A-Z]{2,3}-\d{4}/g)
    if (plates?.[0]) result.truck_head_plate = plates[0]
    if (plates?.[1]) result.truck_body_plate = plates[1]
    // 姓名（在身份證前）
    const nameMatch = text.match(/([^\s，,]+)\s*[，,]?\s*[A-Z][12]\d{8}/)
    if (nameMatch) result.driver_name = nameMatch[1]
    return result
  }

  // 送出聯單
  async function handleSubmit() {
    setIsSubmitting(true)
    setError(null)
    try {
      const res = await formApi.createManifest(systemFields, extracted)
      setManifestId(res.manifest_id)
      setSubmitDone(true)
      // 更新系統欄位中的聯單狀態
      setSystemFields(prev => ({ ...prev, manifest_status: 1, manifest_number: res.manifest_number }))
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  // 匯出 PDF
  async function handleExportPdf() {
    if (!manifestId) return
    try {
      const blob = await formApi.exportPdf(manifestId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `tuflow_${manifestId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('PDF 匯出失敗：' + err.message)
    }
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '360px 1fr',
      height: 'calc(100vh - var(--nav-h))',
      overflow: 'hidden',
    }}>
      {/* ── 左側：A 類系統欄位 ── */}
      <div style={{
        background: 'var(--surface)',
        borderRight: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column', overflow: 'hidden',
      }}>
        {/* 頁首 */}
        <div style={{ padding: '16px 20px 13px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
          <div className="module-tag" style={{ marginBottom: 7 }}>▦ NLP · 電子聯單</div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-hi)', marginBottom: 2 }}>
            系統欄位（A 類）
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted2)' }}>
            系統自動帶入，唯讀顯示
          </div>
        </div>

        {/* 聯單標頭 */}
        <div style={{ padding: '12px 20px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <span style={{ fontFamily: "'Fraunces',serif", fontSize: 14, color: 'var(--text-hi)' }}>
              電子聯單
            </span>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 5,
              fontFamily: "'DM Mono',monospace", fontSize: 10, padding: '3px 9px', borderRadius: 20,
              background: systemFields.manifest_status === 0 ? 'var(--amber-glow)' : 'var(--green-glow)',
              border: `1px solid ${systemFields.manifest_status === 0 ? 'rgba(251,191,36,.25)' : 'var(--green-dim)'}`,
              color: systemFields.manifest_status === 0 ? 'var(--amber)' : 'var(--green)',
            }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor', animation: 'pulse 1.2s ease-in-out infinite' }} />
              {STATUS_LABELS[systemFields.manifest_status] || '未知狀態'}
            </div>
          </div>
          <div style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: 'var(--muted)' }}>
            {systemFields.manifest_number || '待核配聯單序號'}
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '8px 14px' }}>
          {/* 系統欄位列表 */}
          {[
            { label: '工程名稱', val: systemFields.project_name },
            { label: '出土流向編號', val: systemFields.project_code },
            { label: '收容場所代碼', val: systemFields.disposal_site_code },
            { label: '收容場所名稱', val: systemFields.disposal_site_name },
            { label: '土質代碼',     val: systemFields.soil_code },
            { label: '申報土方量',   val: systemFields.total_volume_m3 ? `${systemFields.total_volume_m3} m³` : null },
          ].map(({ label, val }) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '7px 0', borderBottom: '1px solid var(--border)',
              fontSize: 12,
            }}>
              <span style={{ color: 'var(--muted2)' }}>{label}</span>
              <span style={{ fontWeight: 600, color: val ? 'var(--text-hi)' : 'var(--muted)', maxWidth: '55%', textAlign: 'right', wordBreak: 'break-all' }}>
                {val || '—'}
              </span>
            </div>
          ))}

          {/* 可選路線 */}
          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.7px', marginBottom: 6 }}>
              可選運送路線
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {(systemFields.route_list || []).map(r => (
                <span key={r} style={{
                  fontSize: 11, padding: '3px 9px', borderRadius: 20,
                  border: `1px solid ${extracted.route_name === r ? 'var(--green-dim)' : 'var(--border)'}`,
                  background: extracted.route_name === r ? 'var(--green-glow)' : 'var(--surface2)',
                  color: extracted.route_name === r ? 'var(--green)' : 'var(--muted2)',
                }}>
                  {r}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── 右側：B 類填入區 ── */}
      <div style={{ overflowY: 'auto', padding: '20px 26px', background: 'var(--bg)' }}>
        {/* 頁首 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 18, paddingBottom: 14, borderBottom: '1px solid var(--border)' }}>
          <div>
            <h2 style={{ fontFamily: "'Fraunces',serif", fontSize: 19, color: 'var(--text-hi)', marginBottom: 3 }}>
              語音／文字自動填單
            </h2>
            <p style={{ fontSize: 11, color: 'var(--muted2)' }}>B 類欄位（駕駛資訊、出土量、車號）</p>
          </div>
          {submitDone && (
            <button className="btn btn-ghost btn-sm" onClick={handleExportPdf}>
              📄 匯出 PDF
            </button>
          )}
        </div>

        {/* 輸入框 + 語音按鈕 */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.7px', marginBottom: 8 }}>
            自然語言輸入
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
            <textarea
              style={{
                flex: 1, background: 'var(--surface2)', border: '1px solid var(--border)',
                borderRadius: 8, padding: '10px 13px', color: 'var(--text-hi)',
                fontSize: 13, fontFamily: "'Noto Sans TC',sans-serif",
                resize: 'none', outline: 'none', lineHeight: 1.6, minHeight: 72,
              }}
              placeholder="例：路線一，12.5方，王大明，A123456789，車號KAA-1234，車斗KAA-5678"
              value={rawInput}
              onChange={e => setRawInput(e.target.value)}
            />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <VoiceInput onTranscript={handleVoiceTranscript} isDisabled={isExtracting} />
              <button
                className="btn btn-primary btn-sm"
                onClick={handleExtract}
                disabled={isExtracting || !rawInput.trim()}
                style={{ padding: '6px 10px', fontSize: 11 }}
              >
                {isExtracting ? '⟳' : '解析'}
              </button>
            </div>
          </div>
          <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 4 }}>
            🎤 語音輸入後自動填入上方文字框，再點「解析」
          </div>
        </div>

        {/* 錯誤提示 */}
        {error && (
          <div style={{
            marginBottom: 12, padding: '8px 12px',
            background: 'rgba(248,113,113,.1)', border: '1px solid rgba(248,113,113,.25)',
            borderRadius: 6, fontSize: 11.5, color: 'var(--danger)',
          }}>
            ⚠ {error}
          </div>
        )}

        {/* B 類欄位表單 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
          {[
            { key: 'route_name',       label: '出場路線',     placeholder: '路線一' },
            { key: 'actual_volume_m3', label: '實際出土量 (m³)', placeholder: '12.5', type: 'number' },
            { key: 'driver_name',      label: '駕駛人姓名',   placeholder: '王大明' },
            { key: 'driver_id',        label: '駕駛人身份證', placeholder: 'A123456789' },
            { key: 'truck_head_plate', label: '車頭車號',     placeholder: 'KAA-1234' },
            { key: 'truck_body_plate', label: '車斗車號',     placeholder: 'KAA-5678' },
          ].map(({ key, label, placeholder, type }) => {
            const val = extracted[key]
            const conf = confidence[key]
            return (
              <div key={key}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.4px' }}>
                    {label}
                  </span>
                  {conf && (
                    <span style={{ fontSize: 9, color: conf > 0.8 ? 'var(--green)' : conf > 0.5 ? 'var(--amber)' : 'var(--danger)' }}>
                      {Math.round(conf * 100)}%
                    </span>
                  )}
                </div>
                <input
                  className="form-input"
                  type={type || 'text'}
                  value={val || ''}
                  placeholder={placeholder}
                  onChange={e => setExtracted(prev => ({ ...prev, [key]: e.target.value }))}
                  style={{
                    borderColor: val ? 'var(--green-dim)' : 'var(--border)',
                    background: val ? 'rgba(74,222,128,.04)' : 'var(--surface2)',
                  }}
                />
              </div>
            )
          })}
        </div>

        {/* 缺少欄位提示 */}
        {missingFields.length > 0 && (
          <div style={{
            marginBottom: 12, padding: '8px 12px',
            background: 'rgba(251,191,36,.06)', border: '1px solid rgba(251,191,36,.2)',
            borderRadius: 6, fontSize: 11.5, color: 'var(--amber)',
          }}>
            ⚠ 尚未提取到：{missingFields.join('、')}
          </div>
        )}

        {/* 送出按鈕 */}
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={isSubmitting || submitDone || Object.keys(extracted).length === 0}
            style={{ flex: 1 }}
          >
            {isSubmitting ? '⟳ 送出中...' : submitDone ? '✓ 已送出' : '📋 送出聯單'}
          </button>
          <button
            className="btn btn-ghost"
            onClick={() => { setExtracted({}); setConfidence({}); setRawInput(''); setSubmitDone(false); setManifestId(null) }}
          >
            清除
          </button>
        </div>
      </div>
    </div>
  )
}
