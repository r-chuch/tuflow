/**
 * TuFlow API 服務層
 * 統一 fetch wrapper，處理錯誤與 baseURL
 */

const BASE_URL = '/api'  // Vite proxy 會轉發到 http://localhost:8000

// ─── 通用請求函式 ──────────────────────────────────────────────
async function request(method, path, body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body) options.body = JSON.stringify(body)

  const res = await fetch(`${BASE_URL}${path}`, options)

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `API 錯誤 ${res.status}`)
  }

  return res.json()
}

const get    = (path)         => request('GET',   path)
const post   = (path, body)   => request('POST',  path, body)
const patch  = (path, body)   => request('PATCH', path, body)

// ─── 智慧媒合 API ──────────────────────────────────────────────
export const matchApi = {
  /** 取得所有工地 */
  getSites: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return get(`/match/sites${qs ? '?' + qs : ''}`)
  },

  /** 新增工地 */
  createSite: (data) => post('/match/sites', data),

  /** 執行 AI 媒合 */
  runMatch: (supplyId, maxResults = 5, filters = {}) =>
    post('/match/run', {
      supply_id: supplyId,
      max_results: maxResults,
      filters,
    }),

  /** 更新媒合狀態 */
  updateMatchStatus: (matchId, status) =>
    patch(`/match/matches/${matchId}`, { status }),

  /** 取得媒合記錄清單 */
  getMatches: () => get('/match/matches'),

  /** 取得 Demo 資料 */
  getDemo: () => get('/match/demo'),
}

// ─── 自動填單 API ──────────────────────────────────────────────
export const formApi = {
  /** 從文字/語音提取欄位 */
  extract: (rawText, source = 'text', systemFields = {}) =>
    post('/form/extract', {
      raw_text: rawText,
      source,
      system_fields: systemFields,
    }),

  /** 建立聯單 */
  createManifest: (systemFields, extractedFields, matchId = null) =>
    post('/form/create', {
      system_fields: systemFields,
      extracted_fields: extractedFields,
      match_id: matchId,
    }),

  /** 更新聯單 */
  updateManifest: (manifestId, extractedFields) =>
    patch(`/form/manifests/${manifestId}`, { extracted_fields: extractedFields }),

  /** 取得聯單詳情 */
  getManifest: (manifestId) => get(`/form/manifests/${manifestId}`),

  /** 匯出 PDF（回傳 Blob）*/
  exportPdf: async (manifestId) => {
    const res = await fetch(`${BASE_URL}/form/manifests/${manifestId}/export-pdf`)
    if (!res.ok) throw new Error('PDF 匯出失敗')
    return res.blob()
  },

  /** 取得 Demo 聯單 */
  getDemo: () => get('/form/demo'),
}

// ─── 法規問答 API ──────────────────────────────────────────────
export const ragApi = {
  /** 查詢問答 */
  query: (question, topK = 5) =>
    post('/rag/query', { question, top_k: topK }),

  /** 法規資料庫狀態 */
  getStatus: () => get('/rag/status'),

  /** 重新向量化法規（管理員）*/
  ingest: (filepath) =>
    post('/rag/ingest', { filepath }),
}

// ─── 系統健康檢查 ──────────────────────────────────────────────
export const healthApi = {
  check: () => fetch('/health').then(r => r.json()),
}
