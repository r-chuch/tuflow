/**
 * 法條引用元件（可點擊展開原文）
 */
import { useState } from 'react'

// 條文類型標籤
const TYPE_LABEL = {
  penalty:    { text: '罰則', color: 'var(--danger)' },
  procedure:  { text: '程序', color: 'var(--blue)' },
  obligation: { text: '義務', color: 'var(--amber)' },
  general:    { text: '一般', color: 'var(--muted2)' },
}

// 來源標籤（中央 / 地方）
const AUTH_LABEL = {
  local:   { text: '地方', color: 'var(--green)' },
  central: { text: '中央', color: 'var(--muted2)' },
}

/** 單筆法條引用（可展開） */
function LawRefItem({ citation, source }) {
  const [isOpen, setIsOpen] = useState(false)

  // 優先顯示 ChromaDB 完整原文；退而顯示 LLM 提供的 excerpt
  const fullText = source?.full_text || citation.excerpt || null
  const hasText  = Boolean(fullText)

  const typeInfo = TYPE_LABEL[citation.article_type] || TYPE_LABEL.general
  const authInfo = AUTH_LABEL[citation.authority]    || AUTH_LABEL.central
  const similarity = source?.similarity != null
    ? `${Math.round(source.similarity * 100)}%`
    : null

  return (
    <div
      onClick={() => hasText && setIsOpen(o => !o)}
      style={{
        borderRadius: 6,
        border: '1px solid var(--border)',
        background: isOpen ? 'var(--surface2)' : 'var(--surface)',
        transition: 'background .15s',
        cursor: hasText ? 'pointer' : 'default',
        overflow: 'hidden',
      }}
    >
      {/* ── 標題行 ── */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6,
        padding: '7px 10px',
      }}>
        {/* 法規名稱 */}
        <span style={{ fontSize: 11.5, color: 'var(--muted2)', flex: 1, minWidth: 0 }}>
          {citation.law_name}
        </span>

        {/* 條號 */}
        <span className="law-cite" style={{ flexShrink: 0 }}>
          {citation.article_num || citation.article}
        </span>

        {/* 類型標籤 */}
        <span style={{
          fontSize: 9, padding: '1px 5px', borderRadius: 3, flexShrink: 0,
          color: typeInfo.color, border: `1px solid ${typeInfo.color}`,
          opacity: .8,
        }}>
          {typeInfo.text}
        </span>

        {/* 來源標籤 */}
        <span style={{ fontSize: 9, color: authInfo.color, flexShrink: 0, opacity: .7 }}>
          {authInfo.text}
        </span>

        {/* 相似度 */}
        {similarity && (
          <span style={{ fontSize: 9, color: 'var(--muted)', flexShrink: 0 }}>
            {similarity}
          </span>
        )}

        {/* 展開箭頭 */}
        {hasText && (
          <span style={{
            fontSize: 10, color: 'var(--muted)', flexShrink: 0,
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform .2s',
            display: 'inline-block',
          }}>
            ▾
          </span>
        )}
      </div>

      {/* ── 展開：完整條文原文 ── */}
      {isOpen && hasText && (
        <div style={{
          borderTop: '1px solid var(--border)',
          padding: '10px 12px',
          animation: 'fadeIn .18s ease',
        }}>
          <div style={{
            fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase',
            letterSpacing: '.5px', marginBottom: 6,
          }}>
            原文條文
          </div>
          <div style={{
            fontSize: 12,
            lineHeight: 1.85,
            color: 'var(--text)',
            whiteSpace: 'pre-wrap',
            fontFamily: "'Noto Serif TC', serif",
            background: 'var(--bg)',
            borderRadius: 5,
            padding: '8px 11px',
            borderLeft: '3px solid var(--amber)',
          }}>
            {fullText}
          </div>

          {/* 若是 LLM excerpt（非 ChromaDB 完整原文），顯示提示 */}
          {!source?.full_text && citation.excerpt && (
            <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 5, fontStyle: 'italic' }}>
              ※ 顯示為 AI 摘錄，非完整條文原文
            </div>
          )}
        </div>
      )}
    </div>
  )
}


/**
 * 法條引用清單（顯示在訊息下方）
 * lawRefs: LLM 引用的法條（含 article_num、excerpt…）
 * sources:  ChromaDB 實際檢索到的原文段落（含 full_text）
 */
export function LawRefList({ lawRefs = [], sources = [] }) {
  if (!lawRefs || lawRefs.length === 0) return null

  // 建立 sources 查找表：key = "law_name_article_num"
  const sourceMap = {}
  sources.forEach(s => {
    const key = `${s.law_name}_${s.article_num}`
    sourceMap[key] = s
  })

  return (
    <div style={{
      background: 'var(--bg)',
      border: '1px solid var(--border)',
      borderRadius: 8,
      padding: '9px 10px',
      marginTop: 7,
      display: 'flex',
      flexDirection: 'column',
      gap: 5,
    }}>
      <div style={{
        fontSize: 10, fontWeight: 700, color: 'var(--muted)',
        textTransform: 'uppercase', letterSpacing: '.5px',
        marginBottom: 4,
        display: 'flex', alignItems: 'center', gap: 5,
      }}>
        <span>📚 法條引用</span>
        <span style={{ color: 'var(--muted)', fontWeight: 400 }}>
          · 點擊條目展開原文
        </span>
      </div>

      {lawRefs.map((citation, i) => {
        const key = `${citation.law_name}_${citation.article_num || citation.article}`
        const source = sourceMap[key] || null
        return <LawRefItem key={i} citation={citation} source={source} />
      })}
    </div>
  )
}


/**
 * 行內法條引用高亮（inline 用途，不展開）
 */
export default function LawCitation({ lawName, articleNum, excerpt }) {
  return (
    <span
      className="law-cite"
      title={excerpt || `${lawName} ${articleNum}`}
      style={{ cursor: excerpt ? 'help' : 'default' }}
    >
      {articleNum}
    </span>
  )
}
