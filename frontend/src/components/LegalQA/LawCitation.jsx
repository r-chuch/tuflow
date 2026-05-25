/**
 * 法條引用高亮元件
 * 顯示琥珀色 §XX 標籤
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

/**
 * 法條引用清單（顯示在訊息下方）
 */
export function LawRefList({ lawRefs = [] }) {
  if (!lawRefs || lawRefs.length === 0) return null

  return (
    <div style={{
      background: 'var(--bg)',
      border: '1px solid var(--border)',
      borderRadius: 7,
      padding: 10,
      marginTop: 7,
    }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.5px', marginBottom: 7 }}>
        📚 法條引用
      </div>
      {lawRefs.map((ref, i) => (
        <div key={i} style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
          padding: '5px 0',
          borderBottom: i < lawRefs.length - 1 ? '1px solid var(--border)' : 'none',
          fontSize: 11.5,
        }}>
          <div>
            <span style={{ color: 'var(--muted2)' }}>{ref.law_name}</span>
            {' '}
            <span className="law-cite">{ref.article_num || ref.article}</span>
          </div>
          {ref.excerpt && (
            <div style={{
              fontSize: 10.5,
              color: 'var(--muted)',
              maxWidth: '55%',
              textAlign: 'right',
              lineHeight: 1.5,
              fontStyle: 'italic',
            }}>
              「{ref.excerpt.slice(0, 40)}...」
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
