import { useEffect, useRef, useCallback } from 'react'
import { Terminal as XTerm } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'

interface TerminalProps {
  height?: string
}

export default function Terminal({ height = '300px' }: TerminalProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const terminalRef = useRef<XTerm | null>(null)
  const fitAddonRef = useRef<FitAddon | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const inputBufferRef = useRef('')

  const connectWs = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/terminal/ws`)
    ws.onopen = () => {
      terminalRef.current?.writeln('\x1b[32mConnected to terminal\x1b[0m')
    }
    ws.onmessage = (event) => {
      const data = event.data as string
      if (data.startsWith('EXIT:')) {
        terminalRef.current?.writeln(`\x1b[33mProcess exited with code ${data.slice(5)}\x1b[0m`)
        return
      }
      terminalRef.current?.write(data)
    }
    ws.onclose = () => {
      terminalRef.current?.writeln('\x1b[31mDisconnected from terminal\x1b[0m')
      setTimeout(connectWs, 3000)
    }
    ws.onerror = () => ws.close()
    wsRef.current = ws
  }, [])

  useEffect(() => {
    if (!containerRef.current) return
    const term = new XTerm({
      cursorBlink: true,
      cursorStyle: 'block',
      fontSize: 14,
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      theme: {
        background: '#0a1a0a',
        foreground: '#e0f0e0',
        cursor: '#22c55e',
        selectionBackground: '#22c55e44',
        black: '#000000',
        red: '#ef4444',
        green: '#22c55e',
        yellow: '#eab308',
        blue: '#3b82f6',
        magenta: '#a855f7',
        cyan: '#06b6d4',
        white: '#e0f0e0',
        brightBlack: '#4a4a4a',
        brightRed: '#ef4444',
        brightGreen: '#4ade80',
        brightYellow: '#facc15',
        brightBlue: '#60a5fa',
        brightMagenta: '#c084fc',
        brightCyan: '#22d3ee',
        brightWhite: '#ffffff',
      },
    })
    const fitAddon = new FitAddon()
    term.loadAddon(fitAddon)
    term.open(containerRef.current)
    fitAddon.fit()
    terminalRef.current = term
    fitAddonRef.current = fitAddon

    term.onData((data) => {
      if (data === '\r') {
        const cmd = inputBufferRef.current
        inputBufferRef.current = ''
        if (cmd.trim() && wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(cmd)
        }
      } else if (data === '\x7f') {
        inputBufferRef.current = inputBufferRef.current.slice(0, -1)
        term.write('\b \b')
      } else {
        inputBufferRef.current += data
        term.write(data)
      }
    })

    const resizeObserver = new ResizeObserver(() => {
      fitAddon.fit()
    })
    resizeObserver.observe(containerRef.current)

    connectWs()

    return () => {
      resizeObserver.disconnect()
      wsRef.current?.close()
      term.dispose()
    }
  }, [connectWs])

  return (
    <div className="terminal-wrapper">
      <div ref={containerRef} style={{ height }} />
    </div>
  )
}
