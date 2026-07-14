import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Code2, Sparkles } from 'lucide-react'

export default function Welcome() {
  const navigate = useNavigate()
  const [showContent, setShowContent] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return
    video.play().catch(() => {
      video.muted = true
      video.play()
      const unblock = () => {
        video.muted = false
        document.removeEventListener('pointerdown', unblock, true)
      }
      document.addEventListener('pointerdown', unblock, { once: true, capture: true })
    })
    const timer = setTimeout(() => {
      video.pause()
      const audio = audioRef.current
      if (audio) { audio.currentTime = 0; audio.play().catch(() => {}) }
      setShowContent(true)
    }, 14000)
    video.addEventListener('error', () => { clearTimeout(timer); setShowContent(true) }, { once: true })
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="welcome">
      <video ref={videoRef} className="welcome-video" autoPlay playsInline preload="auto">
        <source src="/bg_intro.mp4" type="video/mp4" />
      </video>

      <audio ref={audioRef} src="/Ultronvoice.mp3" preload="auto" />

      {showContent && (
        <>
          <div className="welcome-overlay" />
          <div className="welcome-content">
            <div className="welcome-logo">
              <Code2 size={48} />
              <h1>CODEBUDDY</h1>
            </div>
            <p className="welcome-tagline">Your AI-powered multi-agent coding assistant</p>
            <div className="welcome-features">
              <div className="wf-item"><Sparkles size={16} />Multi-agent orchestration</div>
              <div className="wf-item"><Sparkles size={16} />Smart code analysis</div>
              <div className="wf-item"><Sparkles size={16} />Real-time collaboration</div>
            </div>
            <button className="welcome-cta" onClick={() => navigate('/dashboard')}>
              Enter CODEBUDDY
            </button>
          </div>
        </>
      )}
    </div>
  )
}
