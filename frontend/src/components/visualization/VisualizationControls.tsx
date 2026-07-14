import { useState, useCallback, useRef, useEffect } from 'react'
import { Play, Pause, SkipBack, SkipForward, RotateCcw, Gauge, Wand2, Zap } from 'lucide-react'

interface ControlsProps {
  totalSteps: number
  currentStep: number
  isPlaying: boolean
  speed: number
  onStepPrev: () => void
  onStepNext: () => void
  onPlayPause: () => void
  onRestart: () => void
  onSpeedChange: (speed: number) => void
  onVisualize: () => void
  onRun: () => void
  isGenerating: boolean
  hasCode: boolean
}

export default function VisualizationControls({
  totalSteps,
  currentStep,
  isPlaying,
  speed,
  onStepPrev,
  onStepNext,
  onPlayPause,
  onRestart,
  onSpeedChange,
  onVisualize,
  onRun,
  isGenerating,
  hasCode,
}: ControlsProps) {
  const [showSpeed, setShowSpeed] = useState(false)
  const speedRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (speedRef.current && !speedRef.current.contains(e.target as Node)) setShowSpeed(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const speedLabel = useCallback((s: number) => {
    if (s <= 250) return '0.25x'
    if (s <= 500) return '0.5x'
    if (s <= 750) return '0.75x'
    return '1x'
  }, [])

  return (
    <div className="viz-controls">
      <div className="viz-controls-left">
        <button className="btn btn-sm viz-run-btn" onClick={onRun} disabled={isGenerating || !hasCode}>
          <Zap size={14} />
          Run Code
        </button>
        <button className="btn btn-sm viz-viz-btn" onClick={onVisualize} disabled={isGenerating || !hasCode}>
          <Wand2 size={14} />
          {isGenerating ? 'Generating...' : 'Visualize Code'}
        </button>
      </div>

      <div className="viz-controls-center">
        <button className="viz-ctrl-btn" onClick={onStepPrev} disabled={currentStep <= 0} title="Previous Step">
          <SkipBack size={16} />
        </button>
        <button className="viz-ctrl-btn viz-play-btn" onClick={onPlayPause} disabled={totalSteps === 0} title={isPlaying ? 'Pause' : 'Play'}>
          {isPlaying ? <Pause size={18} /> : <Play size={18} />}
        </button>
        <button className="viz-ctrl-btn" onClick={onStepNext} disabled={currentStep >= totalSteps - 1} title="Next Step">
          <SkipForward size={16} />
        </button>
        <button className="viz-ctrl-btn" onClick={onRestart} disabled={totalSteps === 0} title="Restart">
          <RotateCcw size={16} />
        </button>

        <div className="viz-step-indicator">
          {totalSteps > 0 ? `Step ${currentStep + 1} of ${totalSteps}` : 'No trace'}
        </div>
      </div>

      <div className="viz-controls-right" ref={speedRef}>
        <button className="viz-ctrl-btn" onClick={() => setShowSpeed(!showSpeed)} title="Execution Speed">
          <Gauge size={16} />
          <span className="speed-label">{speedLabel(speed)}</span>
        </button>
        {showSpeed && (
          <div className="viz-speed-popup">
            <div className="speed-title">Execution Speed</div>
            <input
              type="range"
              min={100}
              max={1000}
              step={50}
              value={1200 - speed}
              onChange={(e) => onSpeedChange(1200 - Number(e.target.value))}
            />
            <div className="speed-labels">
              <span>Fast</span>
              <span>Slow</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
