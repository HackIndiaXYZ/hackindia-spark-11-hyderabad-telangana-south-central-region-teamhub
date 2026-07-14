import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FolderKanban, MessageSquare, Bot, Activity } from 'lucide-react'
import { api } from '../api'
import type { Project, ChatHistory } from '../types'

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const [chats, setChats] = useState<ChatHistory[]>([])
  const [stats, setStats] = useState({ projects: 0, chats: 0, messages: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.projects.list(),
      api.chat.list(),
      api.viz.activity('default', 30),
    ]).then(([p, c, s]) => {
      setProjects(p || [])
      setChats(c || [])
      setStats(s)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page"><div className="loading">Loading...</div></div>

  return (
    <div className="page">
      <h2>Dashboard</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <FolderKanban size={24} />
          <div>
            <span className="stat-value">{stats.projects}</span>
            <span className="stat-label">Projects</span>
          </div>
        </div>
        <div className="stat-card">
          <MessageSquare size={24} />
          <div>
            <span className="stat-value">{stats.chats}</span>
            <span className="stat-label">Chats</span>
          </div>
        </div>
        <div className="stat-card">
          <Bot size={24} />
          <div>
            <span className="stat-value">{stats.messages}</span>
            <span className="stat-label">Messages</span>
          </div>
        </div>
        <div className="stat-card">
          <Activity size={24} />
          <div>
            <span className="stat-value">{projects.length}</span>
            <span className="stat-label">Active</span>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dash-section">
          <div className="section-header">
            <h3>Recent Projects</h3>
            <Link to="/projects" className="btn-sm">View All</Link>
          </div>
          <div className="dash-list">
            {projects.slice(0, 5).map((p) => (
              <Link key={p.id} to={`/projects/${p.id}`} className="dash-item">
                <FolderKanban size={16} />
                <div>
                  <strong>{p.name}</strong>
                  <small>{p.language}</small>
                </div>
              </Link>
            ))}
            {projects.length === 0 && <p className="empty">No projects yet</p>}
          </div>
        </div>

        <div className="dash-section">
          <div className="section-header">
            <h3>Recent Chats</h3>
            <Link to="/chat" className="btn-sm">View All</Link>
          </div>
          <div className="dash-list">
            {chats.slice(0, 5).map((c) => (
              <Link key={c.id} to={`/chat/${c.id}`} className="dash-item">
                <MessageSquare size={16} />
                <div>
                  <strong>{c.title}</strong>
                  <small>{new Date(c.updated_at).toLocaleDateString()}</small>
                </div>
              </Link>
            ))}
            {chats.length === 0 && <p className="empty">No chats yet</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
