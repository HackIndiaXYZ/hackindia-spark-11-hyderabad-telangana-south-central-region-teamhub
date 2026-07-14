import type { ApproachInfo, AlgorithmDetection } from '../../types'

interface Props {
  approaches: ApproachInfo | null
  detection: AlgorithmDetection | null
  timeComplexity: string
  spaceComplexity: string
}

export default function Approachespanel({ approaches, detection, timeComplexity, spaceComplexity }: Props) {
  if (!detection && !approaches) {
    return (
      <div className="exec-details">
        <div className="exec-details-header">
          <h3>Better Approaches</h3>
        </div>
        <div className="exec-details-empty">
          <p>Visualize your code to see approach analysis</p>
        </div>
      </div>
    )
  }

  const algoName = detection?.detected || approaches?.algorithm || 'General Approach'
  const tc = approaches?.time_complexity || timeComplexity
  const sc = approaches?.space_complexity || spaceComplexity
  const alts = approaches?.alternatives || []

  return (
    <div className="exec-details">
      <div className="exec-details-header">
        <h3>Better Approaches</h3>
      </div>

      {detection && (
        <div className="exec-section">
          <div className="exec-section-title">Detected Technique</div>
          <div className="exec-algo-name">{algoName}</div>
          <div className="exec-info-row">
            <span className="exec-label">Confidence</span>
            <span className="exec-value">
              <div className="exec-confidence-bar-wrap">
                <div className="exec-confidence-bar" style={{width: `${detection.confidence}%`}} />
              </div>
              <span className="exec-confidence-text">{detection.confidence}%</span>
            </span>
          </div>
          <div className="exec-explanation" style={{marginTop: 8}}>{detection.reason}</div>
        </div>
      )}

      <div className="exec-section">
        <div className="exec-section-title">Current Approach</div>
        <div className="exec-info-row">
          <span className="exec-label">Algorithm</span>
          <span className="exec-value">{algoName}</span>
        </div>
        <div className="exec-info-row">
          <span className="exec-label">Time Complexity</span>
          <span className="exec-value exec-complexity">{tc || 'O(n)'}</span>
        </div>
        <div className="exec-info-row">
          <span className="exec-label">Space Complexity</span>
          <span className="exec-value exec-complexity">{sc || 'O(1)'}</span>
        </div>
      </div>

      {alts.length > 0 && (
        <div className="exec-section">
          <div className="exec-section-title">Alternative Approaches</div>
          {alts.map((alt, i) => (
            <div key={i} className="exec-alt-card">
              <div className="exec-alt-header">
                <span className="exec-alt-name">{alt.algorithm}</span>
                <div className="exec-alt-complexities">
                  <span className="exec-alt-tc">{alt.time_complexity}</span>
                  <span className="exec-alt-sc">{alt.space_complexity}</span>
                </div>
              </div>
              <p className="exec-alt-desc">{alt.explanation}</p>
              {alt.why_faster && (
                <div className="exec-alt-detail">
                  <span className="exec-alt-detail-label">Why faster:</span> {alt.why_faster}
                </div>
              )}
              {alt.additional_memory && (
                <div className="exec-alt-detail">
                  <span className="exec-alt-detail-label">Memory:</span> {alt.additional_memory}
                </div>
              )}
              <div className="exec-alt-when">
                <div className="exec-alt-when-item">
                  <span className="exec-alt-when-label">Current better:</span> {alt.when_current_better}
                </div>
                <div className="exec-alt-when-item">
                  <span className="exec-alt-when-label">Alternative better:</span> {alt.when_alternative_better}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
