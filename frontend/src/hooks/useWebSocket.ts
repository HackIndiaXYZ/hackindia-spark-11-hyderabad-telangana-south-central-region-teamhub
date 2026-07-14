import { useEffect, useState, useCallback } from 'react'
import { wsService } from '../services/websocket'

export function useWebSocket() {
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const unsub = wsService.onStatus((c) => setConnected(c))
    wsService.connect()
    return () => {
      unsub()
      wsService.disconnect()
    }
  }, [])

  const send = useCallback((type: string, payload?: Record<string, unknown>) => {
    wsService.send(type, payload)
  }, [])

  const subscribe = useCallback((type: string, handler: (data: unknown) => void) => {
    return wsService.on(type, handler)
  }, [])

  return { connected, send, subscribe }
}
