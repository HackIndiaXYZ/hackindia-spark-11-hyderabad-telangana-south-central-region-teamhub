import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import Welcome from './pages/Welcome'
import Dashboard from './pages/Dashboard'
import ChatPage from './pages/Chat'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import Agents from './pages/Agents'
import CoderAgentPage from './pages/agents/CoderAgentPage'
import DebuggerAgentPage from './pages/agents/DebuggerAgentPage'
import ArchitectAgentPage from './pages/agents/ArchitectAgentPage'
import ReviewerAgentPage from './pages/agents/ReviewerAgentPage'
import DocumenterAgentPage from './pages/agents/DocumenterAgentPage'
import TesterAgentPage from './pages/agents/TesterAgentPage'
import RefactorerAgentPage from './pages/agents/RefactorerAgentPage'
import ExplainerAgentPage from './pages/agents/ExplainerAgentPage'
import CodeVisualization from './pages/CodeVisualization'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/chat/:chatId" element={<ChatPage />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:id" element={<ProjectDetail />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/agents/coder" element={<CoderAgentPage />} />
            <Route path="/agents/debugger" element={<DebuggerAgentPage />} />
            <Route path="/agents/architect" element={<ArchitectAgentPage />} />
            <Route path="/agents/reviewer" element={<ReviewerAgentPage />} />
            <Route path="/agents/documenter" element={<DocumenterAgentPage />} />
            <Route path="/agents/tester" element={<TesterAgentPage />} />
            <Route path="/agents/refactorer" element={<RefactorerAgentPage />} />
            <Route path="/agents/explainer" element={<ExplainerAgentPage />} />
            <Route path="/visualize" element={<CodeVisualization />} />
          </Route>
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
  </StrictMode>,
)
