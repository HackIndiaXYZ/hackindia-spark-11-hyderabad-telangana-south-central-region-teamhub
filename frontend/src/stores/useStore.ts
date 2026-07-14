import { create } from 'zustand'
import type { Project, ChatHistory } from '../types'

interface AppState {
  projects: Project[]
  chats: ChatHistory[]
  currentChat: ChatHistory | null
  selectedProject: Project | null
  sidebarOpen: boolean
  loading: boolean
  setProjects: (projects: Project[]) => void
  setChats: (chats: ChatHistory[]) => void
  setCurrentChat: (chat: ChatHistory | null) => void
  setSelectedProject: (project: Project | null) => void
  setSidebarOpen: (open: boolean) => void
  setLoading: (loading: boolean) => void
}

export const useStore = create<AppState>((set) => ({
  projects: [],
  chats: [],
  currentChat: null,
  selectedProject: null,
  sidebarOpen: true,
  loading: false,
  setProjects: (projects) => set({ projects }),
  setChats: (chats) => set({ chats }),
  setCurrentChat: (chat) => set({ currentChat: chat }),
  setSelectedProject: (project) => set({ selectedProject: project }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setLoading: (loading) => set({ loading }),
}))
