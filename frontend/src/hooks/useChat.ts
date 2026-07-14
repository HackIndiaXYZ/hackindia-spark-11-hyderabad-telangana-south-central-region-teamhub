import { useState, useCallback, useRef } from 'react'
import { api } from '../api'
import type { Message } from '../types'

interface UseChatOptions {
  onStream?: (chunk: string) => void
}

export function useChat(chatId?: string, _options?: UseChatOptions) {
  const [messages, setMessages] = useState<Message[]>([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const send = useCallback(async (input: string): Promise<string | null> => {
    if (!input.trim() || sending) return null
    const userMsg: Message = { role: 'user', content: input }
    setMessages((m) => [...m, userMsg])
    setSending(true)
    setError(null)
    try {
      const res = await api.chat.send(input, chatId)
      const assistantMsg: Message = { role: 'assistant', content: res.message }
      setMessages((m) => [...m, assistantMsg])
      return res.chat_id || null
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : 'Failed to send message'
      setError(errMsg)
      return null
    } finally {
      setSending(false)
    }
  }, [chatId, sending])

  const cancel = useCallback(() => {
    abortRef.current?.abort()
    setSending(false)
  }, [])

  const clear = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, setMessages, sending, error, send, cancel, clear }
}
