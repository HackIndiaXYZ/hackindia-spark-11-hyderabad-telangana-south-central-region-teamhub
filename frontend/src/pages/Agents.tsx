import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ExternalLink, Play, GitMerge, Code2, Bug, Building2, Search, FileText, FlaskConical, RefreshCw, BookOpen, TestTube } from 'lucide-react'
import { api } from '../api'
import Loading from '../components/Loading'
import MarkdownRenderer from '../components/MarkdownRenderer'
import type { AgentInfo } from '../types'

const iconMap: Record<string, any> = {
  Code2, Bug, Building2, Search, FileText, FlaskConical, RefreshCw, BookOpen, TestTube,
}

export default function Agents() {
  const navigate = useNavigate()
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [request, setRequest] = useState('')
  const [mode, setMode] = useState<'single' | 'orchestrate'>('single')
  const [selected, setSelected] = useState<string>('')
  const [executing, setExecuting] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [showResult, setShowResult] = useState(false)

  useEffect(() => {
    api.agents.list().then((list) => {
      setAgents(list)
      if (list.length > 0) setSelected(list[0].key)
      setLoading(false)
    })
  }, [])

  const run = async () => {
    if (!request.trim()) return
    setExecuting(true)
    setResult(null)
    setShowResult(true)
    try {
      const res = mode === 'single'
        ? await api.agents.execute(request, [selected])
        : await api.agents.orchestrate(request)
      setResult(res)
    } catch (e: any) {
      setResult({ error: e.message })
    } finally { setExecuting(false) }
  }

  const current = agents.find(a => a.key === selected)

  if (loading) return <Loading fullPage text="Loading agents..." />

  return (
    <div className="page">
      <div className="page-header">
        <h2>AI Agents</h2>
        <div className="page-header-actions">
          <div className="agent-mode-toggle">
            <button className={`btn-sm ${mode === 'single' ? 'active' : ''}`} onClick={() => { setMode('single'); setShowResult(false) }}>
              <Play size={14} /> Single
            </button>
            <button className={`btn-sm ${mode === 'orchestrate' ? 'active' : ''}`} onClick={() => { setMode('orchestrate'); setShowResult(false) }}>
              <GitMerge size={14} /> Orchestrate
            </button>
          </div>
        </div>
      </div>

      <div className="agent-grid">
        {agents.map((a) => {
          const Icon = iconMap[a.icon || 'Code2'] || Code2
          const isActive = mode === 'single' && selected === a.key
          return (
            <div
              key={a.key}
              className={`agent-card ${isActive ? 'selected' : ''}`}
              style={{ '--agent-color': a.color || '#22c55e' } as React.CSSProperties}
            >
              <div className="agent-card-content" onClick={() => { setSelected(a.key); setMode('single'); setShowResult(false) }}>
                <div className="agent-card-icon"><Icon size={24} /></div>
                <div className="agent-card-body">
                  <h4>{a.name}</h4>
                  <p>{a.description}</p>
                </div>
              </div>
              <div className="agent-card-footer">
                <button className="btn-sm agent-open-btn" onClick={() => navigate(`/agents/${a.key}`)}>
                  <ExternalLink size={14} /> Open
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {mode === 'orchestrate' && (
        <div className="card orchestrate-info">
          <GitMerge size={18} />
          <span>Orchestration will run all agents in sequence and merge their outputs</span>
        </div>
      )}

      <div className="agent-workspace">
        <div className="workspace-header">
          <h3>{mode === 'single' ? (current?.name || 'Agent') : 'Orchestrator'}</h3>
          {current && <span className="badge" style={{ background: current.color + '22', color: current.color }}>{current.key}</span>}
        </div>
        <textarea
          className="agent-input"
          placeholder={`Describe what you want the ${mode === 'single' ? 'agent' : 'agents'} to do...`}
          value={request}
          onChange={(e) => setRequest(e.target.value)}
          rows={4}
          disabled={executing}
        />
        <button className="btn" onClick={run} disabled={executing || !request.trim()}>
          {executing ? 'Running...' : <><Play size={18} /> {mode === 'single' ? 'Execute Agent' : 'Start Orchestration'}</>}
        </button>
      </div>

      {showResult && result && (
        <div className="agent-result">
          <h3>Result</h3>
          {result.error ? (
            <p className="error">{result.error}</p>
          ) : mode === 'single' ? (
            <div>
              <div className="result-meta">
                <span><strong>Agent:</strong> {result.agent_name}</span>
                <span><strong>Time:</strong> {result.execution_time_ms}ms</span>
                <span><strong>Tokens:</strong> {result.tokens_used}</span>
              </div>
              <MarkdownRenderer content={result.output} />
            </div>
          ) : (
            <div>
              <div className="result-meta">
                <span><strong>Agents:</strong> {result.agents_used?.join(', ')}</span>
                <span><strong>Total:</strong> {result.total_time_ms}ms</span>
              </div>
              {result.results?.map((r: any, i: number) => (
                <details key={i} open={i === 0}>
                  <summary>{r.agent_name} <span className="badge">{r.execution_time_ms}ms</span></summary>
                  <MarkdownRenderer content={r.output} />
                </details>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
