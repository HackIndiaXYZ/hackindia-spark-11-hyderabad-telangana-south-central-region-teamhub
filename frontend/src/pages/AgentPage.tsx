import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft, Play, History, Settings, Clock, Zap,
  MessageSquare, Copy, RotateCcw, Download, Star,
  BarChart3, Network, FileText, Search, Trash2, Pin, Lightbulb,
  Code2, Bug, Building2, FlaskConical, RefreshCw, BookOpen, TestTube,
  ChevronDown, ChevronRight, Terminal, Database, Eye, Lock, Unlock,
  Bookmark, Share2, Minimize2,
} from 'lucide-react'
import { api } from '../api'
import Loading from '../components/Loading'
import CodeEditor from '../components/CodeEditor'
import MarkdownRenderer from '../components/MarkdownRenderer'
import { formatDate, formatTime } from '../utils/format'
import type { AgentInfo } from '../types'

const ICON_MAP: Record<string, typeof Code2> = {
  Code2, Bug, Building2, Search, FileText, FlaskConical, RefreshCw, BookOpen, TestTube,
}

interface AgentPageProps {
  agentKey: string
}

interface Session {
  id: string
  title: string
  timestamp: string
  messages: number
  pinned: boolean
}

interface AgentStats {
  totalExecutions: number
  totalTokens: number
  avgLatency: number
  successRate: number
  lastRun: string | null
}

export default function AgentPage({ agentKey }: AgentPageProps) {
  const [agent, setAgent] = useState<AgentInfo | null>(null)
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [request, setRequest] = useState('')
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  const [executing, setExecuting] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'history' | 'stats' | 'settings' | 'prompt' | 'logs'>('chat')
  const [showExamples, setShowExamples] = useState(false)
  const [sessions] = useState<Session[]>([])
  const [stats, setStats] = useState<AgentStats>({
    totalExecutions: 0, totalTokens: 0, avgLatency: 0, successRate: 100, lastRun: null,
  })
  const [showSettings, setShowSettings] = useState(false)
  const [settings, setSettings] = useState({
    temperature: 0.7, maxTokens: 2048, systemPrompt: '', streamingEnabled: true,
  })
  const [streamedOutput, setStreamedOutput] = useState('')
  const [logLines, setLogLines] = useState<string[]>([])
  const [pinnedSessions, setPinnedSessions] = useState<string[]>([])
  const [bookmarkedSessions, setBookmarkedSessions] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [showGraph, setShowGraph] = useState(false)

  useEffect(() => {
    api.agents.list().then(setAgents).catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    const found = agents.find(a => a.key === agentKey)
    if (found) {
      setAgent(found)
      setSettings(prev => ({ ...prev, systemPrompt: found.system_prompt || '' }))
    }
    setLoading(false)
  }, [agents, agentKey])

  const addLog = useCallback((msg: string) => {
    setLogLines(prev => [...prev, `[${new Date().toISOString()}] ${msg}`].slice(-100))
  }, [])

  const execute = async () => {
    if (!request.trim() || executing) return
    setExecuting(true)
    setResult(null)
    setStreamedOutput('')
    addLog(`Executing ${agent?.name || agentKey} agent...`)
    const start = performance.now()
    try {
      const res = await api.agents.execute(request, [agentKey])
      setResult(res as Record<string, unknown>)
      setStreamedOutput((res as Record<string, unknown>)?.output as string || '')
      const elapsed = performance.now() - start
      setStats(prev => ({
        totalExecutions: prev.totalExecutions + 1,
        totalTokens: prev.totalTokens + ((res as Record<string, unknown>)?.tokens_used as number || 0),
        avgLatency: prev.totalExecutions === 0 ? elapsed : (prev.avgLatency * prev.totalExecutions + elapsed) / (prev.totalExecutions + 1),
        successRate: 100,
        lastRun: new Date().toISOString(),
      }))
      addLog(`Execution completed in ${formatTime(elapsed)}`)
    } catch (e) {
      setResult({ error: (e as Error).message })
      addLog(`Execution failed: ${(e as Error).message}`)
    } finally {
      setExecuting(false)
    }
  }

  const togglePin = (sessionId: string) => {
    setPinnedSessions(prev => prev.includes(sessionId) ? prev.filter(s => s !== sessionId) : [...prev, sessionId])
  }

  const toggleBookmark = (sessionId: string) => {
    setBookmarkedSessions(prev => prev.includes(sessionId) ? prev.filter(s => s !== sessionId) : [...prev, sessionId])
  }

  const filteredSessions = sessions.filter(s =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const pinned = filteredSessions.filter(s => pinnedSessions.includes(s.id))
  const unpinned = filteredSessions.filter(s => !pinnedSessions.includes(s.id))
  const sortedSessions = [...pinned, ...unpinned]

  if (loading) return <Loading fullPage text="Loading agent..." />
  if (!agent) return <div className="page"><p>Agent not found</p></div>

  const Icon = ICON_MAP[agent.icon || 'Code2'] || Code2
  const isPinned = (sessionId: string) => pinnedSessions.includes(sessionId)
  const isBookmarked = (sessionId: string) => bookmarkedSessions.includes(sessionId)

  return (
    <div className="agent-page">
      <div className="agent-page-header">
        <div className="agent-page-title">
          <Link to="/agents" className="back-link"><ArrowLeft size={16} /> Agents</Link>
          <div className="agent-badge" style={{ '--agent-color': agent.color || '#22c55e' } as React.CSSProperties}>
            <Icon size={20} />
            <div>
              <h1>{agent.name}</h1>
              <span className="agent-key-label">{agent.key}</span>
            </div>
          </div>
        </div>
        <div className="agent-page-actions">
          <button className={`btn-sm ${showSettings ? 'active' : ''}`} onClick={() => setShowSettings(!showSettings)}>
            <Settings size={14} /> Settings
          </button>
          <button className="btn-sm" onClick={() => setShowGraph(!showGraph)}>
            <Network size={14} /> Graph
          </button>
        </div>
      </div>

      <p className="agent-description">{agent.description}</p>

      <div className="agent-tabs">
        {(['chat', 'history', 'stats', 'prompt', 'logs'] as const).map(tab => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'chat' && <MessageSquare size={14} />}
            {tab === 'history' && <History size={14} />}
            {tab === 'stats' && <BarChart3 size={14} />}
            {tab === 'prompt' && <FileText size={14} />}
            {tab === 'logs' && <Terminal size={14} />}
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'chat' && (
        <div className="agent-chat-section">
          <div className="agent-examples">
            <button className="btn-sm" onClick={() => setShowExamples(!showExamples)}>
              <Lightbulb size={14} /> Examples {showExamples ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
            {showExamples && (
              <div className="examples-list">
                {agent.key === 'coder' && (
                  <>
                    <button className="example-chip" onClick={() => setRequest('Write a Python function to merge two sorted arrays')}>Merge sorted arrays</button>
                    <button className="example-chip" onClick={() => setRequest('Create a React component for a data table with sorting and filtering')}>React data table</button>
                    <button className="example-chip" onClick={() => setRequest('Write a REST API endpoint in FastAPI for user authentication')}>FastAPI auth endpoint</button>
                  </>
                )}
                {agent.key === 'debugger' && (
                  <>
                    <button className="example-chip" onClick={() => setRequest('Find the bug in this code: function add(a,b){return a-b}')}>Find the bug</button>
                    <button className="example-chip" onClick={() => setRequest('Why is my React component re-rendering infinitely?')}>Infinite re-render</button>
                  </>
                )}
                {agent.key === 'architect' && (
                  <>
                    <button className="example-chip" onClick={() => setRequest('Design a microservices architecture for an e-commerce platform')}>E-commerce architecture</button>
                    <button className="example-chip" onClick={() => setRequest('Design the database schema for a multi-tenant SaaS application')}>SaaS database schema</button>
                  </>
                )}
                {agent.key !== 'coder' && agent.key !== 'debugger' && agent.key !== 'architect' && (
                  <button className="example-chip" onClick={() => setRequest(`Perform your ${agent.name} role on the following code...`)}>General request</button>
                )}
              </div>
            )}
          </div>

          <div className="agent-input-area">
            <textarea
              className="agent-input"
              placeholder={`Describe what you want the ${agent.name} agent to do...`}
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) execute() }}
              rows={4}
              disabled={executing}
            />
            <div className="agent-input-actions">
              <span className="input-hint">{executing ? 'Executing...' : 'Cmd+Enter to run'}</span>
              <button className="btn" onClick={execute} disabled={executing || !request.trim()}>
                {executing ? <><Zap size={16} className="spin" /> Running...</> : <><Play size={16} /> Execute</>}
              </button>
            </div>
          </div>

          {result && (
            <div className="agent-result-card">
              <div className="result-header">
                <h3>Result</h3>
                <div className="result-actions">
                  <button className="btn-sm" onClick={() => navigator.clipboard.writeText(streamedOutput)}>
                    <Copy size={14} /> Copy
                  </button>
                  <button className="btn-sm" onClick={() => setResult(null)}>
                    <RotateCcw size={14} /> Clear
                  </button>
                </div>
              </div>
              <div className="result-meta">
                <span><Zap size={14} /> {(result as Record<string, unknown>)?.execution_time_ms as number || 0}ms</span>
                <span><Database size={14} /> {(result as Record<string, unknown>)?.tokens_used as number || 0} tokens</span>
                <span><Eye size={14} /> {(result as Record<string, unknown>)?.status as string}</span>
              </div>
              {(result as Record<string, unknown>)?.error ? (
                <div className="error-box">{(result as Record<string, unknown>).error as string}</div>
              ) : (
                <div className="result-output-area">
                  <MarkdownRenderer content={streamedOutput} />
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="agent-history-section">
          <div className="history-toolbar">
            <div className="search-bar">
              <Search size={14} />
              <input
                placeholder="Search sessions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="history-filters">
              <button className={`btn-sm ${pinnedSessions.length > 0 ? 'active' : ''}`}>
                <Pin size={14} /> Pinned ({pinnedSessions.length})
              </button>
              <button className={`btn-sm ${bookmarkedSessions.length > 0 ? 'active' : ''}`}>
                <Bookmark size={14} /> Saved ({bookmarkedSessions.length})
              </button>
            </div>
          </div>
          {sortedSessions.length === 0 && (
            <div className="empty-state">
              <History size={40} />
              <h3>No sessions yet</h3>
              <p>Execute a task to see your session history here</p>
            </div>
          )}
          <div className="session-list">
            {sortedSessions.map(session => (
              <div key={session.id} className={`session-item ${isPinned(session.id) ? 'pinned' : ''}`}>
                <div className="session-info">
                  <h4>{session.title}</h4>
                  <div className="session-meta">
                    <span><Clock size={12} /> {formatDate(session.timestamp)}</span>
                    <span><MessageSquare size={12} /> {session.messages} messages</span>
                  </div>
                </div>
                <div className="session-actions">
                  <button className={`icon-btn ${isPinned(session.id) ? 'active' : ''}`} onClick={() => togglePin(session.id)} title="Pin">
                    <Pin size={14} />
                  </button>
                  <button className={`icon-btn ${isBookmarked(session.id) ? 'active' : ''}`} onClick={() => toggleBookmark(session.id)} title="Bookmark">
                    <Star size={14} />
                  </button>
                  <button className="icon-btn" title="Share"><Share2 size={14} /></button>
                  <button className="icon-btn" title="Export"><Download size={14} /></button>
                  <button className="icon-btn" title="Delete"><Trash2 size={14} /></button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="agent-stats-section">
          <div className="stats-grid-4">
            <div className="stat-card">
              <Zap size={20} />
              <div><span className="stat-value">{stats.totalExecutions}</span><span className="stat-label">Executions</span></div>
            </div>
            <div className="stat-card">
              <Database size={20} />
              <div><span className="stat-value">{stats.totalTokens}</span><span className="stat-label">Tokens</span></div>
            </div>
            <div className="stat-card">
              <Clock size={20} />
              <div><span className="stat-value">{formatTime(stats.avgLatency)}</span><span className="stat-label">Avg Latency</span></div>
            </div>
            <div className="stat-card">
              <BarChart3 size={20} />
              <div><span className="stat-value">{stats.successRate}%</span><span className="stat-label">Success Rate</span></div>
            </div>
          </div>
          <div className="agent-info-card">
            <h3>Agent Information</h3>
            <div className="info-grid">
              <div><span>Name</span><span>{agent.name}</span></div>
              <div><span>Key</span><span>{agent.key}</span></div>
              <div><span>Description</span><span>{agent.description}</span></div>
              <div><span>Icon</span><span>{agent.icon}</span></div>
              <div><span>Color</span><span><span className="color-dot" style={{ background: agent.color }} />{agent.color}</span></div>
              <div><span>Last Run</span><span>{stats.lastRun ? formatDate(stats.lastRun) : 'Never'}</span></div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'prompt' && (
        <div className="agent-prompt-section">
          <div className="card">
            <h3>System Prompt</h3>
            <CodeEditor
              value={settings.systemPrompt}
              onChange={(v) => setSettings(prev => ({ ...prev, systemPrompt: v }))}
              language="markdown"
              height="200px"
            />
          </div>
          <div className="card">
            <h3>Execution Settings</h3>
            <div className="settings-grid">
              <div className="setting">
                <label>Temperature</label>
                <div className="setting-control">
                  <input
                    type="range" min="0" max="2" step="0.1"
                    value={settings.temperature}
                    onChange={(e) => setSettings(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                  />
                  <span className="setting-value">{settings.temperature}</span>
                </div>
              </div>
              <div className="setting">
                <label>Max Tokens</label>
                <div className="setting-control">
                  <input
                    type="range" min="256" max="8192" step="256"
                    value={settings.maxTokens}
                    onChange={(e) => setSettings(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                  />
                  <span className="setting-value">{settings.maxTokens}</span>
                </div>
              </div>
              <div className="setting">
                <label>Streaming</label>
                <div className="setting-control">
                  <button
                    className={`toggle ${settings.streamingEnabled ? 'active' : ''}`}
                    onClick={() => setSettings(prev => ({ ...prev, streamingEnabled: !prev.streamingEnabled }))}
                  >
                    {settings.streamingEnabled ? <Unlock size={14} /> : <Lock size={14} />}
                    {settings.streamingEnabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="agent-logs-section">
          <div className="log-toolbar">
            <h3>Execution Logs</h3>
            <button className="btn-sm" onClick={() => setLogLines([])}><Trash2 size={14} /> Clear</button>
          </div>
          <div className="log-viewer">
            {logLines.length === 0 && (
              <div className="empty-state">
                <Terminal size={40} />
                <h3>No logs yet</h3>
                <p>Execute a task to see live logs here</p>
              </div>
            )}
            {logLines.map((line, i) => (
              <div key={i} className="log-line">{line}</div>
            ))}
          </div>
        </div>
      )}

      {showGraph && (
        <div className="agent-graph-overlay" onClick={() => setShowGraph(false)}>
          <div className="agent-graph-panel" onClick={(e) => e.stopPropagation()}>
            <div className="graph-header">
              <h3><Network size={16} /> Execution Graph</h3>
              <button className="icon-btn" onClick={() => setShowGraph(false)}><Minimize2 size={16} /></button>
            </div>
            <div className="graph-content">
              <div className="graph-node start">
                <span>Request</span>
              </div>
              <div className="graph-arrow">↓</div>
              <div className="graph-node" style={{ borderColor: agent.color }}>
                <Icon size={16} />
                <span>{agent.name}</span>
              </div>
              <div className="graph-arrow">↓</div>
              <div className="graph-node end">
                <span>Response</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {showSettings && (
        <div className="settings-panel">
          <div className="settings-header">
            <h3><Settings size={16} /> Agent Settings</h3>
            <button className="icon-btn" onClick={() => setShowSettings(false)}><Minimize2 size={16} /></button>
          </div>
          <div className="settings-body">
            <div className="setting-row">
              <label>Temperature</label>
              <input type="range" min="0" max="2" step="0.1" value={settings.temperature}
                onChange={(e) => setSettings(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))} />
              <span>{settings.temperature}</span>
            </div>
            <div className="setting-row">
              <label>Max Tokens</label>
              <input type="range" min="256" max="8192" step="256" value={settings.maxTokens}
                onChange={(e) => setSettings(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))} />
              <span>{settings.maxTokens}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
