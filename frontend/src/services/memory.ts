import { api } from '../api'

export interface MemoryItem {
  key: string
  text?: string
  value?: string
  score?: number
  agent_name?: string
  project_id?: string
  created_at?: string
  metadata?: Record<string, unknown>
}

export class MemoryService {
  async save(key: string, value: string, agentName?: string): Promise<void> {
    await api.memory.save(key, value, 'default', agentName)
  }

  async search(query: string, topK = 5): Promise<MemoryItem[]> {
    return api.memory.search(query, topK, 'default')
  }

  async getRecent(limit = 10): Promise<MemoryItem[]> {
    return api.memory.recent(limit, 'default')
  }

  async getContext(request: string): Promise<string> {
    const result = await api.memory.context(request, 'default')
    return result.context || ''
  }

  async delete(key: string): Promise<void> {
    await api.memory.delete(key)
  }
}

export const memoryService = new MemoryService()
