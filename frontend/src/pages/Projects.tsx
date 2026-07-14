import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, FolderKanban, ExternalLink, Trash2 } from 'lucide-react'
import { api } from '../api'
import type { Project } from '../types'

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', language: 'python' })
  const navigate = useNavigate()

  const load = () => api.projects.list().then(setProjects).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const create = async (e: React.FormEvent) => {
    e.preventDefault()
    const project = await api.projects.create(form)
    setShowCreate(false)
    setForm({ name: '', description: '', language: 'python' })
    navigate(`/projects/${project.id}`)
  }

  const remove = async (id: string) => {
    await api.projects.delete(id)
    load()
  }

  if (loading) return <div className="page"><div className="loading">Loading...</div></div>

  return (
    <div className="page">
      <div className="page-header">
        <h2>Projects</h2>
        <button className="btn" onClick={() => setShowCreate(true)}>
          <Plus size={18} /> New Project
        </button>
      </div>

      {showCreate && (
        <form className="card create-form" onSubmit={create}>
          <input placeholder="Project name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <input placeholder="Description (optional)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <select value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })}>
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="rust">Rust</option>
            <option value="go">Go</option>
            <option value="java">Java</option>
          </select>
          <div className="form-actions">
            <button type="submit" className="btn">Create</button>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
          </div>
        </form>
      )}

      <div className="project-grid">
        {projects.map((p) => (
          <div key={p.id} className="card project-card">
            <div className="card-header">
              <FolderKanban size={20} />
              <h3>{p.name}</h3>
            </div>
            <p className="card-desc">{p.description || 'No description'}</p>
            <div className="card-meta">
              <span className="badge">{p.language}</span>
              {p.framework && <span className="badge">{p.framework}</span>}
            </div>
            <div className="card-actions">
              <Link to={`/projects/${p.id}`} className="btn-sm">
                <ExternalLink size={14} /> Open
              </Link>
              <button className="btn-sm btn-danger" onClick={() => remove(p.id)}>
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
      {projects.length === 0 && <p className="empty">No projects yet. Create one to get started!</p>}
    </div>
  )
}
