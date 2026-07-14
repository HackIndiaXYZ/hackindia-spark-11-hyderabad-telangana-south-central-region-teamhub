import { useEffect, useState, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, Plus, MessageSquare, Trash2, Square, Brain } from 'lucide-react'
import { api } from '../api'
import type { Message } from '../types'
import { useStore } from '../stores/useStore'
import MemoryPanel from '../components/MemoryPanel'
import MarkdownRenderer from '../components/MarkdownRenderer'

export default function ChatPage() {
  const { chatId } = useParams<{ chatId: string }>()
  const navigate = useNavigate()
  const { chats, setChats, setCurrentChat } = useStore()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [showMemory, setShowMemory] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => { api.chat.list().then(setChats).catch(() => {}) }, [])

  useEffect(() => {
    if (chatId) {
      api.chat.get(chatId).then((chat) => {
        setCurrentChat(chat)
        setMessages(chat.messages || [])
      })
    } else {
      setCurrentChat(null)
      setMessages([])
    }
  }, [chatId])

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, streamingContent])

  const send = useCallback(async () => {
    if (!input.trim() || sending) return
    const userMsg: Message = { role: 'user', content: input }
    setMessages((m) => [...m, userMsg])
    const sentInput = input
    setInput('')
    setSending(true)
    setStreamingContent('')

    const abortController = new AbortController()
    abortRef.current = abortController

    const body = { message: sentInput, stream: true } as Record<string, unknown>
    if (chatId) body.chat_id = chatId

    try {
      const response = await fetch('/api/v1/chat?user_id=default', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: abortController.signal,
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')
      const decoder = new TextDecoder()
      let buffer = ''
      let fullContent = ''
      let newChatId = chatId || ''
      let reading = true

      while (reading) {
        const { done, value } = await reader.read()
        if (done) { reading = false; break }
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.content) {
                fullContent += data.content
                setStreamingContent(fullContent)
              }
              if (data.done) {
                newChatId = data.chat_id || newChatId
                reading = false
              }
            } catch { /* skip incomplete chunk */ }
          }
        }
      }

      if (fullContent) {
        const assistantMsg: Message = { role: 'assistant', content: fullContent }
        setMessages((m) => [...m, assistantMsg])
        if (!chatId && newChatId) navigate(`/chat/${newChatId}`, { replace: true })
        api.chat.list().then(setChats).catch(() => {})
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      const errMsg = err instanceof Error ? err.message : 'Failed'
      const errorMsg: Message = { role: 'assistant', content: `Error: ${errMsg}` }
      setMessages((m) => [...m, errorMsg])
    } finally {
      setSending(false)
      setStreamingContent('')
      abortRef.current = null
    }
  }, [input, sending, chatId, navigate])

  const stop = useCallback(() => {
    abortRef.current?.abort()
    setSending(false)
    if (streamingContent) {
      setMessages((m) => [...m, { role: 'assistant', content: streamingContent }])
    }
    setStreamingContent('')
  }, [streamingContent])

  const newChat = () => {
    setCurrentChat(null)
    setMessages([])
    navigate('/chat')
  }

  const removeChat = async (id: string) => {
    await api.chat.delete(id)
    if (chatId === id) { setCurrentChat(null); setMessages([]); navigate('/chat') }
    api.chat.list().then(setChats).catch(() => {})
  }

  return (
    <div className="chat-page">
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <h3>Chats</h3>
          <button className="btn-sm" onClick={newChat}><Plus size={14} /> New</button>
        </div>
        <div className="chat-list">
          {chats.map((c) => (
            <div key={c.id} className={`chat-list-item ${chatId === c.id ? 'active' : ''}`}
              onClick={() => navigate(`/chat/${c.id}`)}>
              <MessageSquare size={16} />
              <span>{c.title}</span>
              <button className="icon-btn" onClick={(e) => { e.stopPropagation(); removeChat(c.id) }}>
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="chat-main">
        <div className="chat-toolbar">
          <button
            className={`btn-icon ${showMemory ? 'active' : ''}`}
            onClick={() => setShowMemory(!showMemory)}
            title="Toggle memory panel"
          >
            <Brain size={16} />
          </button>
        </div>

        <div className="chat-content">
          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={`message ${m.role}`}>
                <div className="message-avatar">{m.role === 'user' ? 'U' : 'AI'}</div>
                <div className="message-content">
                  <strong>{m.role === 'user' ? 'You' : 'CODEBUDDY'}</strong>
                  {m.role === 'user' ? <p>{m.content}</p> : <MarkdownRenderer content={m.content} />}
                </div>
              </div>
            ))}
            {streamingContent && (
              <div className="message assistant streaming">
                <div className="message-avatar">AI</div>
                <div className="message-content">
                  <strong>CODEBUDDY</strong>
                  <MarkdownRenderer content={streamingContent} />
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          <div className="input-bar">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && !sending && send()}
              placeholder="Ask CODEBUDDY anything..."
              disabled={sending}
            />
            {sending ? (
              <button className="btn btn-danger" onClick={stop}>
                <Square size={18} />
              </button>
            ) : (
              <button className="btn" onClick={send} disabled={!input.trim()}>
                <Send size={18} />
              </button>
            )}
          </div>
        </div>

        {showMemory && (
          <div className="chat-memory-panel">
            <MemoryPanel />
          </div>
        )}
      </div>
    </div>
  )
}
