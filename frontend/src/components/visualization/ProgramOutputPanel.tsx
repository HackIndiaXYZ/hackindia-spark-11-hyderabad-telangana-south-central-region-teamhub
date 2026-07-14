import type { ProgramOutput } from '../../types'

interface Props {
  output: ProgramOutput | null
}

export default function ProgramOutputPanel({ output }: Props) {
  if (!output) {
    return (
      <div className="exec-details">
        <div className="exec-details-header">
          <h3>Program Output</h3>
        </div>
        <div className="exec-details-empty">
          <p>Run your code to see the output</p>
        </div>
      </div>
    )
  }

  const hasContent = output.stdout || output.stderr || output.compile_error || output.runtime_error;

  return (
    <div className="exec-details">
      <div className="exec-details-header">
        <h3>Program Output</h3>
      </div>

      {output.compile_error && (
        <div className="exec-section">
          <div className="exec-section-title warn">Compile Error</div>
          <div className="exec-output-box error">{output.compile_error}</div>
        </div>
      )}

      {output.runtime_error && (
        <div className="exec-section">
          <div className="exec-section-title error">Runtime Error</div>
          <div className="exec-output-box error">{output.runtime_error}</div>
        </div>
      )}

      {output.stderr && (
        <div className="exec-section">
          <div className="exec-section-title">Standard Error</div>
          <pre className="exec-output-box error">{output.stderr}</pre>
        </div>
      )}

      {output.stdout && (
        <div className="exec-section">
          <div className="exec-section-title">Standard Output</div>
          <pre className="exec-output-box">{output.stdout}</pre>
        </div>
      )}

      {!hasContent && (
        <div className="exec-empty-vars" style={{padding: '12px'}}>
          No output was produced
        </div>
      )}

      {hasContent && (
        <div className="exec-section">
          <div className="exec-section-title">Exit & Resource</div>
          <div className="exec-info-row">
            <span className="exec-label">Exit Status</span>
            <span className={`exec-value ${output.exit_status !== 0 ? 'error' : ''}`}>{output.exit_status}</span>
          </div>
          {output.execution_time_ms > 0 && (
            <div className="exec-info-row">
              <span className="exec-label">Time</span>
              <span className="exec-value">{output.execution_time_ms} ms</span>
            </div>
          )}
          {output.memory_usage_kb > 0 && (
            <div className="exec-info-row">
              <span className="exec-label">Memory</span>
              <span className="exec-value">{output.memory_usage_kb} KB</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
