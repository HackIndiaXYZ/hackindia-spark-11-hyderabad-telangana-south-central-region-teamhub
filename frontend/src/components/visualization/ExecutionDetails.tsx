import { useMemo } from 'react'
import type { TraceStep } from '../../types'

interface Props {
  step: TraceStep | null
}

export default function ExecutionDetails({ step }: Props) {
  const vars = useMemo(() => {
    if (!step?.variables) return []
    return Object.entries(step.variables)
  }, [step])

  if (!step) {
    return (
      <div className="exec-details">
        <div className="exec-details-header">
          <h3>Execution Details</h3>
        </div>
        <div className="exec-details-empty">
          <p>Click <strong>Visualize Code</strong> to begin step-by-step execution</p>
        </div>
      </div>
    )
  }

  return (
    <div className="exec-details">
      <div className="exec-details-header">
        <h3>Execution Details</h3>
      </div>

      <div className="exec-section">
        <div className="exec-section-title">Current Step</div>
        <div className="exec-info-row">
          <span className="exec-label">Step</span>
          <span className="exec-value">{step.step}</span>
        </div>
        <div className="exec-info-row">
          <span className="exec-label">Line</span>
          <span className="exec-value">{step.line}</span>
        </div>
        <div className="exec-info-row">
          <span className="exec-label">Operation</span>
          <span className="exec-value exec-op">{step.operation}</span>
        </div>
      </div>

      {step.output && (
        <div className="exec-section">
          <div className="exec-section-title">Output</div>
          <div className="exec-output-box">{step.output}</div>
        </div>
      )}

      <div className="exec-section">
        <div className="exec-section-title">Variables</div>
        {vars.length === 0 ? (
          <div className="exec-empty-vars">No variables yet</div>
        ) : (
          <div className="exec-vars-list">
            {vars.map(([key, val]) => (
              <div key={key} className="exec-var-row">
                <span className="exec-var-name">{key}</span>
                <span className="exec-var-arrow">→</span>
                <span className="exec-var-value">{formatVal(val)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {step.dataStructure && (
        <div className="exec-section">
          <div className="exec-section-title">Data Structure State</div>
          <div className="exec-ds-type">{step.dataStructure.type}</div>
          <div className="exec-ds-values">
            {step.dataStructure.type === 'stack' && (
              <div className="exec-stack-visual">
                {step.dataStructure.values.length === 0 ? (
                  <div className="exec-stack-empty">[ empty ]</div>
                ) : (
                  [...(step.dataStructure.values as number[])].reverse().map((v, i) => (
                    <div key={i} className={`exec-stack-item ${i === 0 ? 'exec-stack-top' : ''}`}>
                      <span>{v}</span>
                      {i === 0 && <span className="exec-stack-top-label">← Top</span>}
                    </div>
                  ))
                )}
                <div className="exec-stack-base">───────</div>
              </div>
            )}
            {step.dataStructure.type === 'queue' && (
              <div className="exec-queue-visual">
                {(step.dataStructure.values as number[]).map((v, i) => (
                  <div key={i} className={`exec-queue-item ${i === 0 ? 'exec-queue-front' : ''} ${i === step.dataStructure!.values.length - 1 ? 'exec-queue-back' : ''}`}>
                    <span>{v}</span>
                    {i === 0 && <span className="exec-queue-label">Front</span>}
                    {i === step.dataStructure!.values.length - 1 && <span className="exec-queue-label">Back</span>}
                  </div>
                ))}
              </div>
            )}
            {step.dataStructure.type === 'array' && (
              <div className="exec-array-visual">
                {(step.dataStructure.values as number[]).map((v, i) => (
                  <div key={i} className={`exec-array-item ${step.highlightedIndexes.includes(i) ? 'highlighted' : ''}`}>
                    {v}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {step.callStack.length > 0 && (
        <div className="exec-section">
          <div className="exec-section-title">Call Stack</div>
          <div className="exec-call-stack">
            {[...step.callStack].reverse().map((frame, i) => (
              <div key={i} className={`exec-stack-frame ${i === 0 ? 'exec-stack-frame-active' : ''}`}>
                {frame}
              </div>
            ))}
          </div>
        </div>
      )}

      {step.complexity && (
        <div className="exec-section">
          <div className="exec-section-title">Complexity</div>
          <div className="exec-info-row">
            <span className="exec-label">Time</span>
            <span className="exec-value exec-complexity">{step.complexity.time}</span>
          </div>
          <div className="exec-info-row">
            <span className="exec-label">Space</span>
            <span className="exec-value exec-complexity">{step.complexity.space}</span>
          </div>
        </div>
      )}

      {step.explanation && (
        <div className="exec-section">
          <div className="exec-section-title">Explanation</div>
          <div className="exec-explanation">{step.explanation}</div>
        </div>
      )}
    </div>
  )
}

function formatVal(val: unknown): string {
  if (val === null) return 'null'
  if (val === undefined) return 'undefined'
  if (typeof val === 'string') return `"${val}"`
  if (Array.isArray(val)) return `[${val.join(', ')}]`
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}
