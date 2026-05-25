/**
 * 聊天訊息氣泡元件
 */
import { LawRefList } from './LawCitation'

export default function ChatMessage({ message }) {
  const { role, text, lawRefs, confidence, suggestedAction, isTyping } = message
  const isUser = role === 'user'

  return (
    <div style={{
      display: 'flex',
      gap: 8,
      alignItems: 'flex-start',
      flexDirection: isUser ? 'row-reverse' : 'row',
      animation: 'fadeIn .25s ease',
    }}>
      {/* 頭像 */}
      <div style={{
        width: 28, height: 28, borderRadius: 7, flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 10, fontWeight: 700, letterSpacing: '.3px',
        background: isUser ? 'var(--surface3)' : 'var(--green-glow)',
        border: `1px solid ${isUser ? 'var(--border-hi)' : 'var(--green-dim)'}`,
        color: isUser ? 'var(--muted2)' : 'var(--green)',
      }}>
        {isUser ? 'YOU' : 'AI'}
      </div>

      {/* 氣泡 */}
      <div style={{ maxWidth: '90%' }}>
        <div style={{
          padding: '9px 12px',
          borderRadius: isUser ? '10px 3px 10px 10px' : '3px 10px 10px 10px',
          fontSize: 12.5,
          lineHeight: 1.7,
          background: isUser ? 'var(--green-glow)' : 'var(--surface2)',
          border: `1px solid ${isUser ? 'var(--green-dim)' : 'var(--border)'}`,
          color: isUser ? 'var(--text-hi)' : 'var(--text)',
        }}>
          {isTyping ? (
            <div style={{ display: 'flex', gap: 4, alignItems: 'center', padding: '3px 0' }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 5, height: 5, borderRadius: '50%',
                  background: 'var(--muted2)',
                  animation: `typingBounce .9s ease-in-out infinite`,
                  animationDelay: `${i * 0.15}s`,
                }} />
              ))}
            </div>
          ) : (
            text
          )}
        </div>

        {/* 法條引用清單 */}
        {!isUser && lawRefs && <LawRefList lawRefs={lawRefs} />}

        {/* 建議動作 */}
        {!isUser && suggestedAction && (
          <div style={{
            marginTop: 6,
            padding: '6px 10px',
            background: 'rgba(96,165,250,.06)',
            border: '1px solid rgba(96,165,250,.15)',
            borderRadius: 6,
            fontSize: 11,
            color: 'var(--blue)',
          }}>
            💡 建議：{suggestedAction}
          </div>
        )}

        {/* 信心度標籤 */}
        {!isUser && confidence && (
          <div style={{ marginTop: 4, fontSize: 10, color: 'var(--muted)', display: 'flex', gap: 5 }}>
            <span>信心度：</span>
            <span style={{
              color: confidence === 'high' ? 'var(--green)' : confidence === 'medium' ? 'var(--amber)' : 'var(--danger)',
            }}>
              {confidence === 'high' ? '高' : confidence === 'medium' ? '中' : '低'}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
