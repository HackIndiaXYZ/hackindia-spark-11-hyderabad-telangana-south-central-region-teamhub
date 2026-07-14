import { useRef } from 'react'
import Editor, { type OnMount } from '@monaco-editor/react'

interface CodeEditorProps {
  value: string
  onChange?: (value: string) => void
  language?: string
  readOnly?: boolean
  height?: string
  minimap?: boolean
}

const LANGUAGE_MAP: Record<string, string> = {
  python: 'python',
  javascript: 'javascript',
  typescript: 'typescript',
  js: 'javascript',
  ts: 'typescript',
  jsx: 'javascript',
  tsx: 'typescript',
  rust: 'rust',
  go: 'go',
  java: 'java',
  cpp: 'cpp',
  c: 'c',
  csharp: 'csharp',
  ruby: 'ruby',
  php: 'php',
  swift: 'swift',
  kotlin: 'kotlin',
  scala: 'scala',
  html: 'html',
  css: 'css',
  scss: 'scss',
  sql: 'sql',
  shell: 'shell',
  bash: 'shell',
  yaml: 'yaml',
  json: 'json',
  xml: 'xml',
  markdown: 'markdown',
  md: 'markdown',
  dockerfile: 'dockerfile',
}

export default function CodeEditor({ value, onChange, language, readOnly = false, height = '400px', minimap = true }: CodeEditorProps) {
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null)

  const handleMount: OnMount = (editor) => {
    editorRef.current = editor
  }

  const mappedLang = LANGUAGE_MAP[language?.toLowerCase() || ''] || 'plaintext'

  return (
    <div className="code-editor-wrapper">
      <Editor
        height={height}
        language={mappedLang}
        value={value}
        onChange={(v) => onChange?.(v || '')}
        onMount={handleMount}
        options={{
          readOnly,
          minimap: { enabled: minimap },
          fontSize: 13,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          wordWrap: 'on',
          padding: { top: 8 },
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        }}
        theme="vs-dark"
      />
    </div>
  )
}
