import type { TraceStep } from '../../types'

interface DSAVisualizerProps {
  step: TraceStep
}

export default function DSAVisualizer({ step }: DSAVisualizerProps) {
  const ds = step.dataStructure
  if (!ds) return <div className="viz-empty">No data to visualize</div>

  switch (ds.type) {
    case 'array':
      return <ArrayViz values={ds.values as number[]} highlighted={step.highlightedIndexes} />
    case 'stack':
      return <StackViz values={ds.values as number[]} operation={step.operation} />
    case 'queue':
      return <QueueViz values={ds.values as number[]} operation={step.operation} />
    case 'linked_list':
      return <LinkedListViz values={ds.values as number[]} highlighted={step.highlightedIndexes} />
    case 'tree':
      return <TreeViz values={ds.values as number[]} root={ds.root as number | undefined} />
    case 'graph':
      return <GraphViz nodes={ds.nodes || []} edges={ds.edges || []} visited={ds.visited || []} current={ds.current ?? null} />
    case 'call_stack':
      return <CallStackViz callStack={step.callStack} />
    default:
      return <ArrayViz values={ds.values as number[]} highlighted={step.highlightedIndexes} />
  }
}

function ArrayViz({ values, highlighted }: { values: number[]; highlighted: number[] }) {
  return (
    <div className="dsa-array-container">
      <div className="dsa-array-label">Array</div>
      <div className="dsa-array">
        {values.map((v, i) => (
          <div
            key={i}
            className={`dsa-array-item ${highlighted.includes(i) ? 'dsa-highlighted' : ''}`}
          >
            <span className="dsa-index">{i}</span>
            <span className="dsa-value">{v}</span>
          </div>
        ))}
      </div>
      <div className="dsa-arrows">
        {values.map((_, i) => (
          i < values.length - 1 && <span key={i} className="dsa-arrow">→</span>
        ))}
      </div>
    </div>
  )
}

function StackViz({ values, operation }: { values: number[]; operation: string }) {
  const reversed = [...values].reverse()
  return (
    <div className="dsa-stack-container">
      <div className="dsa-stack-label">
        Stack {operation === 'push' && <span className="dsa-op-badge dsa-push">push</span>}
        {operation === 'pop' && <span className="dsa-op-badge dsa-pop">pop</span>}
      </div>
      <div className="dsa-stack">
        {reversed.length === 0 ? (
          <div className="dsa-stack-empty">[ empty ]</div>
        ) : (
          reversed.map((v, i) => (
            <div key={i} className={`dsa-stack-item ${i === 0 ? 'dsa-stack-top' : ''}`}>
              <span className="dsa-value">{v}</span>
              {i === 0 && <span className="dsa-top-label">← Top</span>}
            </div>
          ))
        )}
        <div className="dsa-stack-base">─────────</div>
      </div>
    </div>
  )
}

function QueueViz({ values, operation }: { values: number[]; operation: string }) {
  return (
    <div className="dsa-queue-container">
      <div className="dsa-queue-label">
        Queue {operation === 'enqueue' && <span className="dsa-op-badge dsa-enqueue">enqueue</span>}
        {operation === 'dequeue' && <span className="dsa-op-badge dsa-dequeue">dequeue</span>}
      </div>
      <div className="dsa-queue">
        {values.length === 0 ? (
          <div className="dsa-queue-empty">[ empty ]</div>
        ) : (
          <>
            <span className="dsa-queue-label-text">Front</span>
            {values.map((v, i) => (
              <div key={i} className={`dsa-queue-item ${i === 0 ? 'dsa-queue-front' : ''} ${i === values.length - 1 ? 'dsa-queue-back' : ''}`}>
                {v}
              </div>
            ))}
            <span className="dsa-queue-label-text">Back</span>
          </>
        )}
      </div>
    </div>
  )
}

function LinkedListViz({ values, highlighted }: { values: number[]; highlighted: number[] }) {
  return (
    <div className="dsa-linked-list-container">
      <div className="dsa-linked-list-label">Linked List</div>
      <div className="dsa-linked-list">
        {values.map((v, i) => (
          <div key={i} className="dsa-ll-node-wrap">
            <div className={`dsa-ll-node ${highlighted.includes(i) ? 'dsa-highlighted' : ''}`}>
              <span className="dsa-ll-data">{v}</span>
            </div>
            {i < values.length - 1 && <span className="dsa-ll-arrow">→</span>}
          </div>
        ))}
      </div>
      <div className="dsa-null">null</div>
    </div>
  )
}

function TreeViz({ values, root }: { values: number[]; root?: number }) {
  if (values.length === 0) return <div className="dsa-tree-empty">Empty tree</div>

  const sorted = [...values].sort((a, b) => a - b)
  const buildBST = (arr: number[]): TreeNode | null => {
    if (arr.length === 0) return null
    const mid = Math.floor(arr.length / 2)
    return {
      val: arr[mid],
      left: buildBST(arr.slice(0, mid)),
      right: buildBST(arr.slice(mid + 1)),
    }
  }

  interface TreeNode {
    val: number
    left: TreeNode | null
    right: TreeNode | null
  }

  const tree = buildBST(sorted)
  if (!tree) return <div className="dsa-tree-empty">Empty tree</div>

  const renderNode = (node: TreeNode | null, depth: number = 0): React.ReactNode => {
    if (!node) return null
    return (
      <div key={`${node.val}-${depth}`} className="dsa-tree-node-wrap">
        <div className={`dsa-tree-node ${node.val === root ? 'dsa-tree-root' : ''}`}>
          {node.val}
        </div>
        {(node.left || node.right) && (
          <div className="dsa-tree-children">
            <div className="dsa-tree-child">
              {node.left ? (
                <>
                  <div className="dsa-tree-line" />
                  {renderNode(node.left, depth + 1)}
                </>
              ) : (
                <div className="dsa-tree-empty-child" />
              )}
            </div>
            <div className="dsa-tree-child">
              {node.right ? (
                <>
                  <div className="dsa-tree-line" />
                  {renderNode(node.right, depth + 1)}
                </>
              ) : (
                <div className="dsa-tree-empty-child" />
              )}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="dsa-tree-container">
      <div className="dsa-tree-label">Binary Search Tree</div>
      <div className="dsa-tree">
        {renderNode(tree)}
      </div>
    </div>
  )
}

function GraphViz({ nodes, edges, visited, current }: { nodes: string[]; edges: [string, string][]; visited: string[]; current: string | null }) {
  const positions: Record<string, { x: number; y: number }> = {}
  const cx = 150, cy = 120, r = 90
  nodes.forEach((n, i) => {
    const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2
    positions[n] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) }
  })

  return (
    <div className="dsa-graph-container">
      <div className="dsa-graph-label">Graph — BFS Traversal</div>
      <svg width={300} height={260} className="dsa-graph-svg">
        {edges.map(([u, v], i) => {
          const p1 = positions[u]
          const p2 = positions[v]
          if (!p1 || !p2) return null
          const bothVisited = visited.includes(u) && visited.includes(v)
          return <line key={i} x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y} className={`dsa-graph-edge ${bothVisited ? 'dsa-edge-visited' : ''}`} />
        })}
        {nodes.map((n) => {
          const pos = positions[n]
          if (!pos) return null
          const isVisited = visited.includes(n)
          const isCurrent = n === current
          return (
            <g key={n}>
              <circle cx={pos.x} cy={pos.y} r={18} className={`dsa-graph-node ${isCurrent ? 'dsa-graph-current' : isVisited ? 'dsa-graph-visited' : ''}`} />
              <text x={pos.x} y={pos.y + 5} textAnchor="middle" className="dsa-graph-node-text">{n}</text>
            </g>
          )
        })}
      </svg>
      <div className="dsa-graph-legend">
        <span className="dsa-legend-item"><span className="dsa-dot dsa-dot-current" /> Current</span>
        <span className="dsa-legend-item"><span className="dsa-dot dsa-dot-visited" /> Visited</span>
        <span className="dsa-legend-item"><span className="dsa-dot dsa-dot-unvisited" /> Unvisited</span>
      </div>
    </div>
  )
}

function CallStackViz({ callStack }: { callStack: string[] }) {
  return (
    <div className="dsa-callstack-container">
      <div className="dsa-callstack-label">Call Stack</div>
      <div className="dsa-callstack">
        {callStack.length === 0 ? (
          <div className="dsa-callstack-empty">Stack is empty</div>
        ) : (
          [...callStack].reverse().map((frame, i) => (
            <div key={i} className={`dsa-callstack-frame ${i === 0 ? 'dsa-callstack-active' : ''}`}>
              <span className="dsa-callstack-frame-text">{frame}</span>
              {i === 0 && <span className="dsa-callstack-arrow">← top</span>}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
