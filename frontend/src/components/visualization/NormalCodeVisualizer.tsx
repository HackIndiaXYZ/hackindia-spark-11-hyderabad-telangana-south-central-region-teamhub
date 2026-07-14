import { useMemo } from 'react'
import type { TraceStep } from '../../types'

interface Props {
  step: TraceStep | null
  codeLines: string[]
}

const FORMAT: Record<string, (v: unknown) => string> = {
  string: (v) => `"${v}"`,
  number: (v) => String(v),
  boolean: (v) => String(v),
  object: (v) => Array.isArray(v) ? `[${(v as unknown[]).join(', ')}]` : JSON.stringify(v),
}

function fmt(val: unknown): string {
  if (val === null) return 'null'
  if (val === undefined) return 'undefined'
  return (FORMAT[typeof val] || FORMAT.object)(val)
}

export default function NormalCodeVisualizer({ step, codeLines }: Props) {
  const lineElements = useMemo(() =>
    codeLines.map((line, i) => {
      const lineNum = i + 1
      const isActive = step?.line === lineNum
      const isExecuted = !!(step && step.operation !== 'error' && lineNum <= step.line)
      return (
        <div key={i}
          className={`normal-viz-line ${isActive ? 'normal-viz-line-active' : ''} ${isExecuted && lineNum < step.line ? 'normal-viz-line-executed' : ''}`}>
          <span className="normal-viz-line-num">{lineNum}</span>
          <span className="normal-viz-line-code">{line || ' '}</span>
          {isActive && <span className="normal-viz-line-marker">▶</span>}
        </div>
      )
    }),
    [codeLines, step?.line, step?.operation]
  )

  if (!step) {
    return (
      <div className="normal-viz">
        <div className="normal-viz-label">Code Execution Flow</div>
        <div className="normal-viz-empty">No execution trace yet</div>
      </div>
    )
  }

  const vars = Object.entries(step.variables)
  const changedVars = step.changedVariables || []
  const hasChanged = changedVars.length > 0

  return (
    <div className="normal-viz">
      <div className="normal-viz-label">
        Code Execution Flow
        <span className="normal-viz-step-info">Step {step.step} · Line {step.line}</span>
      </div>

      <div className="normal-viz-code-flow">{lineElements}</div>

      {step.operation && step.operation !== 'start' && step.operation !== 'complete' && (
        <div className="normal-viz-operation">
          <span className="normal-viz-op-label">Operation:</span>
          <span className="normal-viz-op-value">{step.operation.replace(/_/g, ' ')}</span>
          {step.loopIteration != null && (
            <span className="normal-viz-iteration">Iteration: {step.loopIteration}</span>
          )}
          {step.conditionResult != null && (
            <span className={`normal-viz-condition ${step.conditionResult ? 'true' : 'false'}`}>
              {step.conditionResult ? '✓ True' : '✗ False'}
            </span>
          )}
        </div>
      )}

      <div className="normal-viz-memory">
        <div className="normal-viz-memory-title">
          Memory / Variables
          {hasChanged && <span className="normal-viz-changed-badge">{changedVars.length} changed</span>}
        </div>
        <div className="normal-viz-memory-box">
          {!vars.length ? (
            <div className="normal-viz-no-vars">No variables yet</div>
          ) : (
            vars.map(([key, val]) => {
              const isChanged = changedVars.includes(key)
              return (
                <div key={key} className={`normal-viz-var-row ${isChanged ? 'normal-viz-var-changed' : ''}`}>
                  <span className="normal-viz-var-name">{key}</span>
                  <span className="normal-viz-var-arrow">→</span>
                  <span className="normal-viz-var-val">{fmt(val)}</span>
                  {isChanged && <span className="normal-viz-var-dot">●</span>}
                </div>
              )
            })
          )}
        </div>
      </div>

      {step.callStack && step.callStack.length > 0 && (
        <div className="normal-viz-memory">
          <div className="normal-viz-memory-title">Call Stack</div>
          <div className="normal-viz-memory-box">
            {[...step.callStack].reverse().map((frame, i) => (
              <div key={i} className={`normal-viz-var-row ${i === 0 ? 'normal-viz-var-changed' : ''}`}>
                <span className="normal-viz-var-name">{i === 0 ? '→' : ''}</span>
                <span className="normal-viz-var-val">{frame}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {step.output && (
        <div className="normal-viz-output">
          <div className="normal-viz-output-title">Console Output</div>
          <div className="normal-viz-output-box">{step.output}</div>
        </div>
      )}

      {step.explanation && (
        <div className="normal-viz-explanation">
          <div className="normal-viz-explanation-title">Explanation</div>
          <div className="normal-viz-explanation-text">{step.explanation}</div>
        </div>
      )}

      {step.operation === 'error' && step.output && (
        <div className="normal-viz-error">
          <div className="normal-viz-error-title">Error</div>
          <div className="normal-viz-error-box">{step.output}</div>
        </div>
      )}
    </div>
  )
}
