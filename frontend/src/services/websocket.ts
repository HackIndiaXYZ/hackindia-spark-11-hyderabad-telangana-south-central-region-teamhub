type MessageHandler = (data: unknown) => void
type StatusHandler = (connected: boolean) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private handlers = new Map<string, Set<MessageHandler>>()
  private statusHandlers = new Set<StatusHandler>()
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private url: string = ''
  private connected = false

  connect(url: string = `ws://${window.location.hostname}:8000/ws/default`) {
    this.url = url
    if (this.ws) this.disconnect()
    this.ws = new WebSocket(url)
    this.ws.onopen = () => {
      this.connected = true
      this.statusHandlers.forEach((h) => h(true))
    }
    this.ws.onclose = () => {
      this.connected = false
      this.statusHandlers.forEach((h) => h(false))
      this.scheduleReconnect()
    }
    this.ws.onerror = () => {
      this.ws?.close()
    }
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        const type = (data as Record<string, unknown>)?.type as string || 'message'
        const handlers = this.handlers.get(type)
        if (handlers) handlers.forEach((h) => h(data))
        const allHandlers = this.handlers.get('*')
        if (allHandlers) allHandlers.forEach((h) => h(data))
      } catch {
        // ignore parse errors
      }
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
    this.connected = false
  }

  send(type: string, payload: Record<string, unknown> = {}) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...payload }))
    }
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) this.handlers.set(type, new Set())
    this.handlers.get(type)!.add(handler)
    return () => this.handlers.get(type)?.delete(handler)
  }

  onStatus(handler: StatusHandler) {
    this.statusHandlers.add(handler)
    return () => this.statusHandlers.delete(handler)
  }

  isConnected() { return this.connected }

  private scheduleReconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      if (!this.connected) this.connect(this.url)
    }, 3000)
  }
}

export const wsService = new WebSocketService()
