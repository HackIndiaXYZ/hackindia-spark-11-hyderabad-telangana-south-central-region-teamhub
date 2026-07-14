import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Plus, FileCode, Trash2 } from 'lucide-react'
import { api } from '../api'
import type { Project, FileItem } from '../types'

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ path: '', content: '', language: '' })

  const load = async () => {
    if (!id) return
    const [p, f] = await Promise.all([api.projects.get(id), api.files.list(id)])
    setProject(p)
    setFiles(f || [])
    setLoading(false)
  }

  useEffect(() => { load() }, [id])

  const createFile = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    await api.files.create(id, form)
    setShowCreate(false)
    setForm({ path: '', content: '', language: '' })
    load()
  }

  const deleteFile = async (fileId: string) => {
    if (!id) return
    await api.files.delete(id, fileId)
    load()
  }

  if (loading) return <div className="page"><div className="loading">Loading...</div></div>
  if (!project) return <div className="page"><p>Project not found</p></div>

  return (
    <div className="page">
      <Link to="/projects" className="back-link"><ArrowLeft size={16} /> Back to Projects</Link>

      <div className="page-header">
        <div>
          <h2>{project.name}</h2>
          <p className="subtitle">{project.description || 'No description'} · <span className="badge">{project.language}</span></p>
        </div>
        <button className="btn" onClick={() => setShowCreate(true)}>
          <Plus size={18} /> Add File
        </button>
      </div>

      {showCreate && (
        <form className="card create-form" onSubmit={createFile}>
          <input placeholder="File path (e.g. src/main.py)" value={form.path} onChange={(e) => setForm({ ...form, path: e.target.value })} required />
          <input placeholder="Language (e.g. python)" value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })} />
          <textarea placeholder="File content (optional)" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} rows={6} />
          <div className="form-actions">
            <button type="submit" className="btn">Create</button>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
          </div>
        </form>
      )}

      <div className="file-list">
        {files.map((f) => (
          <div key={f.id} className="file-item">
            <FileCode size={18} />
            <div className="file-info">
              <strong>{f.path}</strong>
              {f.language && <span className="badge">{f.language}</span>}
            </div>
            <button className="btn-sm btn-danger" onClick={() => deleteFile(f.id)}>
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>
      {files.length === 0 && <p className="empty">No files yet</p>}
    </div>
  )
}
