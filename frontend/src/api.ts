const BASE = '/api/v1'

async function fetchJson(url: string, opts?: RequestInit) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...opts?.headers },
    ...opts,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  projects: {
    list: (userId = 'default') => fetchJson(`/projects?user_id=${userId}`),
    get: (id: string) => fetchJson(`/projects/${id}`),
    create: (data: { name: string; description?: string; language?: string }) =>
      fetchJson('/projects?user_id=default', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: Record<string, unknown>) =>
      fetchJson(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id: string) => fetchJson(`/projects/${id}`, { method: 'DELETE' }),
    stats: (id: string) => fetchJson(`/projects/${id}/stats`),
  },
  files: {
    list: (projectId: string) => fetchJson(`/files/${projectId}`),
    get: (projectId: string, fileId: string) => fetchJson(`/files/${projectId}/${fileId}`),
    create: (projectId: string, data: { path: string; content?: string; language?: string }) =>
      fetchJson(`/files/${projectId}`, { method: 'POST', body: JSON.stringify(data) }),
    update: (projectId: string, fileId: string, data: Record<string, unknown>) =>
      fetchJson(`/files/${projectId}/${fileId}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (projectId: string, fileId: string) =>
      fetchJson(`/files/${projectId}/${fileId}`, { method: 'DELETE' }),
  },
  chat: {
    list: (userId = 'default') => fetchJson(`/chat?user_id=${userId}`),
    get: (chatId: string) => fetchJson(`/chat/${chatId}`),
    send: (message: string, chatId?: string) =>
      fetchJson(`/chat?user_id=default`, {
        method: 'POST',
        body: JSON.stringify({ message, chat_id: chatId, stream: false }),
      }),
    delete: (chatId: string) => fetchJson(`/chat/${chatId}`, { method: 'DELETE' }),
  },
  agents: {
    list: () => fetchJson('/agents/list'),
    execute: (request: string, agents?: string[]) =>
      fetchJson('/agents/execute', {
        method: 'POST',
        body: JSON.stringify({ request, agents }),
      }),
    orchestrate: (request: string, agents?: string[]) =>
      fetchJson('/agents/orchestrate', {
        method: 'POST',
        body: JSON.stringify({ request, agents }),
      }),
  },
  viz: {
    project: (id: string) => fetchJson(`/visualization/project/${id}`),
    activity: (userId = 'default', days = 7) => fetchJson(`/visualization/activity/${userId}?days=${days}`),
    trace: (code: string, language = 'python', algorithm?: string, inputData = '') =>
      fetchJson('/visualization/trace', {
        method: 'POST',
        body: JSON.stringify({ code, language, algorithm, input_data: inputData }),
      }),
    explainStep: (code: string, step: unknown, algorithmType = '', mode = 'beginner') =>
      fetchJson('/visualization/explain-step', {
        method: 'POST',
        body: JSON.stringify({ code, step, algorithm_type: algorithmType, mode }),
      }),
  },
  memory: {
    save: (key: string, value: string, userId = 'default', agentName?: string) =>
      fetchJson(`/memory?key=${encodeURIComponent(key)}&value=${encodeURIComponent(value)}&user_id=${userId}${agentName ? `&agent_name=${encodeURIComponent(agentName)}` : ''}`, { method: 'POST' }),
    search: (query: string, topK = 5, userId = 'default') =>
      fetchJson(`/memory/search?query=${encodeURIComponent(query)}&top_k=${topK}&user_id=${userId}`),
    recent: (limit = 10, userId = 'default') =>
      fetchJson(`/memory/recent?limit=${limit}&user_id=${userId}`),
    context: (request: string, userId = 'default') =>
      fetchJson(`/memory/context?request=${encodeURIComponent(request)}&user_id=${userId}`),
    delete: (key: string) =>
      fetchJson(`/memory/${encodeURIComponent(key)}`, { method: 'DELETE' }),
  },
  stream: {
    chat: (message: string, chatId?: string) => {
      const body: Record<string, unknown> = { message, stream: true }
      if (chatId) body.chat_id = chatId
      return fetch(`${BASE}/chat?user_id=default`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
    },
  },
}
