import type { ReferencesInfo, AlgorithmDetection } from '../../types'

interface Props {
  references: ReferencesInfo | null
  detection: AlgorithmDetection | null
}

export default function ReferencesPanel({ references, detection }: Props) {
  if (!references && !detection) {
    return (
      <div className="exec-details">
        <div className="exec-details-header">
          <h3>Learn & References</h3>
        </div>
        <div className="exec-details-empty">
          <p>Visualize your code to see learning references</p>
        </div>
      </div>
    )
  }

  const refs = references
  const algoName = detection?.detected || 'General'

  if (!refs) {
    return (
      <div className="exec-details">
        <div className="exec-details-header">
          <h3>Learn & References</h3>
        </div>
        <div className="exec-details-empty">
          <p>References not available for this code</p>
        </div>
      </div>
    )
  }

  return (
    <div className="exec-details">
      <div className="exec-details-header">
        <h3>Learn & References</h3>
      </div>

      <div className="exec-section">
        <div className="exec-section-title">Main Concept</div>
        <div className="exec-algo-name">{refs.main_concept || algoName}</div>
      </div>

      {refs.pattern && (
        <div className="exec-section">
          <div className="exec-section-title">Problem-Solving Pattern</div>
          <div className="exec-explanation">{refs.pattern}</div>
        </div>
      )}

      {refs.prerequisites && refs.prerequisites.length > 0 && (
        <div className="exec-section">
          <div className="exec-section-title">Prerequisites</div>
          <div className="exec-tags">
            {refs.prerequisites.map((p, i) => (
              <span key={i} className="exec-tag">{p}</span>
            ))}
          </div>
        </div>
      )}

      {refs.similar_problems && refs.similar_problems.length > 0 && (
        <div className="exec-section">
          <div className="exec-section-title">Similar Problems</div>
          <ul className="exec-list">
            {refs.similar_problems.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </div>
      )}

      {refs.related_topics && refs.related_topics.length > 0 && (
        <div className="exec-section">
          <div className="exec-section-title">Related Topics</div>
          <div className="exec-tags">
            {refs.related_topics.map((t, i) => (
              <span key={i} className="exec-tag exec-tag-related">{t}</span>
            ))}
          </div>
        </div>
      )}

      {refs.practice_problems && refs.practice_problems.length > 0 && (
        <div className="exec-section">
          <div className="exec-section-title">Practice Problems</div>
          <ul className="exec-list">
            {refs.practice_problems.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </div>
      )}

      {refs.pseudocode && (
        <div className="exec-section">
          <div className="exec-section-title">Pseudocode</div>
          <pre className="exec-pseudocode">{refs.pseudocode}</pre>
        </div>
      )}
    </div>
  )
}
