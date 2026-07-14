import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { Code2, MessageSquare, FolderKanban, Bot, PanelLeftClose, PanelLeft, ChevronDown, ChevronRight, Eye } from 'lucide-react'
import { useStore } from '../stores/useStore'
import { useState } from 'react'

const navItems = [
  { to: '/dashboard', icon: Code2, label: 'Dashboard' },
  { to: '/chat', icon: MessageSquare, label: 'Chat' },
  { to: '/projects', icon: FolderKanban, label: 'Projects' },
  { to: '/agents', icon: Bot, label: 'Agents' },
  { to: '/visualize', icon: Eye, label: 'Visualize' },
]

const agentLinks = [
  { to: '/agents/coder', label: 'Coder', icon: 'Code' },
  { to: '/agents/debugger', label: 'Debugger', icon: 'Bug' },
  { to: '/agents/architect', label: 'Architect', icon: 'Building' },
  { to: '/agents/reviewer', label: 'Reviewer', icon: 'Search' },
  { to: '/agents/documenter', label: 'Documenter', icon: 'File' },
  { to: '/agents/tester', label: 'Tester', icon: 'Test' },
  { to: '/agents/refactorer', label: 'Refactorer', icon: 'Refresh' },
  { to: '/agents/explainer', label: 'Explainer', icon: 'Book' },
]

export default function Layout() {
  const { sidebarOpen, setSidebarOpen } = useStore()
  const location = useLocation()
  const [agentsExpanded, setAgentsExpanded] = useState(location.pathname.startsWith('/agents'))

  return (
    <div className="layout">
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h1 className="logo">
            <Code2 size={24} />
            <span>CODEBUDDY</span>
          </h1>
          <button className="icon-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
          </button>
        </div>
        <nav className="nav">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Icon size={20} />
              <span>{label}</span>
            </NavLink>
          ))}
          <div className="nav-group">
            <button className="nav-group-header" onClick={() => setAgentsExpanded(!agentsExpanded)}>
              {agentsExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              <span>Agent Pages</span>
            </button>
            {agentsExpanded && agentLinks.map(({ to, label }) => (
              <NavLink key={to} to={to} className={({ isActive }) => `nav-item sub ${isActive ? 'active' : ''}`}>
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
