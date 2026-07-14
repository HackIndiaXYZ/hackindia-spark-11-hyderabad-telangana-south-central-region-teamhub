import type { TraceStep, AlgorithmDetection } from '../../types'
import DSAVisualizer from './DSAVisualizers'
import NormalCodeVisualizer from './NormalCodeVisualizer'

interface Props {
  step: TraceStep | null
  algorithmType: string
  codeLines: string[]
  detection?: AlgorithmDetection | null
}

const DSA_TYPES = ['array', 'stack', 'queue', 'linked_list', 'tree', 'graph', 'bubble_sort', 'selection_sort', 'insertion_sort', 'linear_search', 'binary_search', 'recursion', 'call_stack', 'merge_sort', 'quick_sort', 'heap_sort', 'counting_sort']

export default function VisualizationPanel({ step, algorithmType, codeLines, detection }: Props) {
  const isDSA = DSA_TYPES.includes(algorithmType) || (step?.dataStructure?.type && ['array', 'stack', 'queue', 'linked_list', 'tree', 'graph', 'call_stack'].includes(step.dataStructure.type))

  if (!step) {
    return (
      <div className="viz-panel">
        <div className="viz-panel-header">
          <h3>Interactive Visualization</h3>
        </div>
        <div className="viz-panel-empty">
          <div className="viz-empty-icon">👁</div>
          <h4>Code Visualization</h4>
          <p>Write or paste your code in the editor, then click <strong>Visualize Code</strong> to see step-by-step execution.</p>
          <div className="viz-empty-features">
            <span>Arrays</span>
            <span>Stacks</span>
            <span>Queues</span>
            <span>Sorting</span>
            <span>Searching</span>
            <span>Trees</span>
            <span>Graphs</span>
            <span>Recursion</span>
          </div>
        </div>
      </div>
    )
  }

  if (step.operation === 'error') {
    return (
      <div className="viz-panel">
        <div className="viz-panel-header">
          <h3>Interactive Visualization</h3>
        </div>
        <div className="viz-panel-error">
          <div className="viz-error-title">Execution Error</div>
          <div className="viz-error-msg">{step.output || step.explanation}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="viz-panel">
      <div className="viz-panel-header">
        <h3>Interactive Visualization</h3>
        <div className="viz-panel-badges">
          <span className="viz-algo-badge">{algorithmType.replace(/_/g, ' ')}</span>
          {detection && detection.confidence > 0 && (
            <span className="viz-detect-badge" title={detection.reason}>
              {detection.detected} ({detection.confidence}%)
            </span>
          )}
        </div>
      </div>
      <div className="viz-panel-content">
        {isDSA ? (
          <DSAVisualizer step={step} />
        ) : (
          <NormalCodeVisualizer step={step} codeLines={codeLines} />
        )}
      </div>
    </div>
  )
}
