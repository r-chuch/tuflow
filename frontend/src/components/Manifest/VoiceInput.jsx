/**
 * 語音輸入元件（使用 Web Speech API）
 */
import { useState, useCallback } from 'react'

export default function VoiceInput({ onTranscript, isDisabled }) {
  const [isRecording, setIsRecording] = useState(false)
  const [recognition,  setRecognition] = useState(null)
  const [supported]    = useState(() => 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  const startRecording = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const rec = new SpeechRecognition()
    rec.lang = 'zh-TW'
    rec.continuous = false
    rec.interimResults = false
    rec.maxAlternatives = 1

    rec.onstart = () => setIsRecording(true)
    rec.onend   = () => { setIsRecording(false); setRecognition(null) }
    rec.onerror = (e) => {
      console.warn('語音識別錯誤：', e.error)
      setIsRecording(false)
    }
    rec.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      onTranscript?.(transcript)
    }

    rec.start()
    setRecognition(rec)
  }, [onTranscript])

  const stopRecording = useCallback(() => {
    recognition?.stop()
    setIsRecording(false)
  }, [recognition])

  if (!supported) {
    return (
      <div style={{ fontSize: 11, color: 'var(--muted)', padding: '6px 10px', background: 'var(--surface2)', borderRadius: 6, border: '1px solid var(--border)' }}>
        ⚠ 您的瀏覽器不支援語音輸入（建議使用 Chrome）
      </div>
    )
  }

  return (
    <button
      onClick={isRecording ? stopRecording : startRecording}
      disabled={isDisabled}
      title={isRecording ? '停止錄音' : '語音輸入'}
      style={{
        width: 36, height: 36,
        borderRadius: 8,
        border: `1px solid ${isRecording ? 'rgba(248,113,113,.4)' : 'var(--border)'}`,
        background: isRecording ? 'rgba(248,113,113,.1)' : 'var(--surface2)',
        color: isRecording ? 'var(--danger)' : 'var(--muted2)',
        fontSize: 14,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: isDisabled ? 'not-allowed' : 'pointer',
        transition: 'all .18s',
        flexShrink: 0,
        position: 'relative',
      }}
    >
      🎤
      {isRecording && (
        <div style={{
          position: 'absolute', top: -2, right: -2,
          width: 8, height: 8, borderRadius: '50%',
          background: 'var(--danger)',
          animation: 'pulse 1.2s ease-in-out infinite',
        }} />
      )}
    </button>
  )
}
